"""ExplanationValidator — structural integrity checks for a computed explanation.

Enforces five rules before any explanation is persisted:
  1. Prediction row exists in the database.
  2. Model in explanation matches the model_id of the prediction.
  3. Feature count equals number of SHAP values.
  4. SHAP value array is a non-empty 1-D list of finite floats.
  5. base_value is a finite float (not NaN, not Inf).

Raises ExplanationValidationError on failure.
"""
import logging
import math
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.prediction import Prediction

logger = logging.getLogger("Explainability.Validator")


class ExplanationValidationError(ValueError):
    """Raised when an explanation fails structural validation."""
    def __init__(self, reasons: List[str]):
        self.reasons = reasons
        super().__init__(f"Explanation validation failed: {'; '.join(reasons)}")


class ExplanationValidator:
    """Validates that a computed explanation is structurally correct and consistent."""

    def __init__(self, db: Session):
        self.db = db

    def validate(
        self,
        prediction_id: UUID,
        model_id: UUID,
        shap_output: Dict[str, Any],
    ) -> None:
        """Run all validation rules.

        Parameters
        ----------
        prediction_id : UUID of the originating Prediction row.
        model_id      : UUID of the active model used for explanation.
        shap_output   : dict returned by SHAPEngine.explain().

        Raises
        ------
        ExplanationValidationError if any rule fails.
        """
        reasons: List[str] = []

        # ── Rule 1: Prediction must exist ──────────────────────────────
        prediction = self.db.get(Prediction, prediction_id)
        if prediction is None:
            reasons.append(
                f"Prediction '{prediction_id}' does not exist in the database."
            )

        # ── Rule 2: Model must match the prediction's model_id ──────────
        if prediction is not None and prediction.model_id != model_id:
            reasons.append(
                f"Explanation model_id '{model_id}' does not match "
                f"prediction.model_id '{prediction.model_id}'. "
                f"The active model may have changed since this prediction was made. "
                f"Explanations can only be generated while the original model remains active."
            )

        # ── Rule 3: Feature count must equal SHAP value count ───────────
        feature_names = shap_output.get("feature_names", [])
        shap_values   = shap_output.get("shap_values", [])
        if len(feature_names) != len(shap_values):
            reasons.append(
                f"Feature count ({len(feature_names)}) does not match "
                f"SHAP value count ({len(shap_values)})."
            )

        # ── Rule 4: SHAP values must be a non-empty 1-D list of floats ──
        if not shap_values:
            reasons.append("SHAP values list is empty.")
        else:
            for i, v in enumerate(shap_values):
                if not isinstance(v, (int, float)):
                    reasons.append(
                        f"SHAP value at index {i} is not numeric: {type(v).__name__}."
                    )
                elif not math.isfinite(float(v)):
                    reasons.append(
                        f"SHAP value at index {i} is non-finite (NaN or Inf)."
                    )

        # ── Rule 5: base_value must be a finite float ───────────────────
        base_value = shap_output.get("base_value")
        if base_value is None:
            reasons.append("base_value is missing from SHAP output.")
        elif not isinstance(base_value, (int, float)):
            reasons.append(
                f"base_value must be numeric, got {type(base_value).__name__}."
            )
        elif not math.isfinite(float(base_value)):
            reasons.append("base_value is non-finite (NaN or Inf).")

        if reasons:
            logger.warning("Explanation validation failed: %s", reasons)
            raise ExplanationValidationError(reasons)

        logger.info(
            "ExplanationValidator: all checks passed for prediction '%s'.", prediction_id
        )
