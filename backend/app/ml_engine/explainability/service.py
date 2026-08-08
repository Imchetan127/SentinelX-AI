"""ExplainabilityService — top-level orchestrator for Sprint 4.1.

Responsibilities
----------------
- Resolve the active model via the existing InferenceService registry path.
- Load the model artifact and scaler (reuses InferenceService._get_model_and_scaler).
- Accept a prediction_id and reconstruct the scaled feature row for the explanation.
- Coordinate SHAPEngine → ExplanationValidator → ExplanationPersistence →
  ExplanationReporter in a single atomic pipeline.
- Emit audit events (EXPLANATION_GENERATED, EXPLANATION_FAILED,
  EXPLANATION_VALIDATED) via AuditIntegration.
- Support re-explaining a prediction (idempotent: stores new row each time
  but returns same SHAP values due to determinism).

Does NOT modify inference logic, governance, or model lifecycle.
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from app.ml_engine.explainability.shap_engine import SHAPEngine, UnsupportedModelError
from app.ml_engine.explainability.validator import ExplanationValidator, ExplanationValidationError
from app.ml_engine.explainability.persistence import ExplanationPersistence
from app.ml_engine.explainability.reporter import ExplanationReporter
from app.ml_engine.explainability.audit import AuditIntegration
from app.ml_engine.inference.engine import InferenceService
from app.models.explanation import Explanation
from app.models.prediction import Prediction
from app.repositories.explanation_repository import ExplanationRepository

from app.core.config import settings

logger = logging.getLogger("Explainability.Service")


class ExplainabilityService:
    """Orchestrates the full SHAP explanation pipeline for a given prediction."""

    def __init__(
        self,
        db:           Session,
        base_dir:     Optional[str] = None,
        datasets_dir: Optional[str] = None,
        top_n:        int = 5,
    ):
        self.db           = db
        self.base_dir     = base_dir or settings.MODEL_DIR
        self.datasets_dir = datasets_dir or settings.DATASETS_DIR

        # Sub-components
        self._shap_engine   = SHAPEngine(top_n=top_n)
        self._validator     = ExplanationValidator(db)
        self._persistence   = ExplanationPersistence(db)
        self._reporter      = ExplanationReporter()
        self._audit         = AuditIntegration(db)
        self._expl_repo     = ExplanationRepository(db)

        # Reuse the existing inference engine for model + scaler resolution.
        # We intentionally do NOT trigger a new prediction — just load the model.
        self._inference     = InferenceService(db, base_dir=base_dir, datasets_dir=datasets_dir)

    # ------------------------------------------------------------------
    # Primary entry point
    # ------------------------------------------------------------------

    def explain_prediction(
        self,
        prediction_id: UUID,
        feature_values: Dict[str, Any],
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Generate a SHAP explanation for an existing prediction.

        Parameters
        ----------
        prediction_id  : UUID of a persisted Prediction row.
        feature_values : Original (unscaled) feature dict used for the prediction.
        user_id        : Authenticated user for audit trail.

        Returns
        -------
        Canonical explanation dict (from ExplanationReporter).
        """
        warnings: List[str] = []

        # ── 1. Verify prediction exists ────────────────────────────────
        prediction = self.db.get(Prediction, prediction_id)
        if prediction is None:
            msg = f"Prediction '{prediction_id}' not found in database."
            self._audit.log_failed(prediction_id, msg, user_id)
            raise FileNotFoundError(msg)

        # ── 2. Resolve active model via registry ───────────────────────
        try:
            model_meta = self._inference._resolve_active_model()
        except RuntimeError as exc:
            self._audit.log_failed(prediction_id, str(exc), user_id)
            raise

        model_id_str = model_meta["model_id"]
        algorithm    = model_meta["algorithm"]
        model_version = model_meta["version"]

        try:
            model_uuid = UUID(model_id_str)
        except ValueError:
            msg = (
                f"Registry model_id '{model_id_str}' is not a valid UUID. "
                f"The model registry entry may be corrupt."
            )
            self._audit.log_failed(prediction_id, msg, user_id)
            raise ValueError(msg)

        # ── 3. Validate model type before attempting SHAP ──────────────
        alg_lower = algorithm.lower().strip()
        if alg_lower not in ("random_forest", "randomforest", "xgboost", "xgb"):
            msg = (
                f"Algorithm '{algorithm}' is not supported for XAI explanations. "
                f"Supported: random_forest, xgboost."
            )
            self._audit.log_failed(prediction_id, msg, user_id)
            raise UnsupportedModelError(msg)

        # ── 4. Load model + scaler (reuses inference cache) ───────────
        try:
            model, scaler, expected_features = self._inference._get_model_and_scaler(model_meta)
        except (FileNotFoundError, RuntimeError) as exc:
            self._audit.log_failed(prediction_id, str(exc), user_id)
            raise

        # ── 5. Reconstruct scaled feature row ─────────────────────────
        # Validate and order features exactly as the model expects
        validation_errors = self._inference.validate_features(feature_values, expected_features)
        if validation_errors:
            msg = f"Feature validation failed: {'; '.join(validation_errors)}"
            self._audit.log_failed(prediction_id, msg, user_id)
            raise ValueError(msg)

        row_df = pd.DataFrame([feature_values], columns=expected_features)
        if scaler is not None:
            scaled_array = scaler.transform(row_df)
            X_scaled = pd.DataFrame(scaled_array, columns=expected_features)
        else:
            X_scaled = row_df

        # ── 6. SHAP computation ────────────────────────────────────────
        try:
            shap_output = self._shap_engine.explain(
                model=model,
                algorithm=algorithm,
                X_scaled=X_scaled,
                feature_names=expected_features,
            )
        except UnsupportedModelError as exc:
            self._audit.log_failed(prediction_id, str(exc), user_id)
            raise
        except RuntimeError as exc:
            self._audit.log_failed(prediction_id, str(exc), user_id)
            raise

        warnings.extend(shap_output.get("warnings", []))

        # ── 7. Validate explanation ────────────────────────────────────
        try:
            self._validator.validate(
                prediction_id=prediction_id,
                model_id=model_uuid,
                shap_output=shap_output,
            )
        except ExplanationValidationError as exc:
            reason = "; ".join(exc.reasons)
            self._audit.log_failed(prediction_id, reason, user_id)
            raise

        self._audit.log_validated(prediction_id, user_id)

        # ── 8. Build explanation document ──────────────────────────────
        explanation_doc = self._reporter.build(
            prediction_id  = prediction_id,
            model_id       = model_uuid,
            model_version  = model_version,
            algorithm      = algorithm,
            prediction     = prediction.prediction,
            confidence     = prediction.confidence,
            shap_output    = shap_output,
            extra_warnings = warnings,
        )

        # ── 9. Persist ─────────────────────────────────────────────────
        try:
            saved = self._persistence.save(
                explanation_doc = explanation_doc,
                model_version   = model_version,
                algorithm       = algorithm,
            )
        except Exception as exc:
            self._audit.log_failed(prediction_id, f"Persistence failed: {exc}", user_id)
            raise

        # ── 10. Audit: generated ────────────────────────────────────────
        self._audit.log_generated(
            prediction_id  = prediction_id,
            explanation_id = str(saved.id),
            algorithm      = algorithm,
            user_id        = user_id,
        )

        explanation_doc["db_explanation_id"] = str(saved.id)
        logger.info(
            "ExplainabilityService: explanation '%s' generated for prediction '%s'.",
            saved.id, prediction_id,
        )
        return explanation_doc

    # ------------------------------------------------------------------
    # History queries
    # ------------------------------------------------------------------

    def get_latest_for_prediction(self, prediction_id: UUID) -> Optional[Explanation]:
        """Return the most recent Explanation row for *prediction_id*."""
        return self._expl_repo.get_latest_for_prediction(prediction_id)

    def list_recent(self, limit: int = 50, offset: int = 0) -> List[Explanation]:
        """Return recent Explanation rows ordered by most recent first."""
        return self._expl_repo.list_recent(limit=limit, offset=offset)
