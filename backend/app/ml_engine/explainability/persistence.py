"""ExplanationPersistence — thin repository wrapper for saving Explanation rows.

Single responsibility: converts a structured explanation dict into an
ORM Explanation object, persists it, and refreshes the row.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.explanation import Explanation

logger = logging.getLogger("Explainability.Persistence")


class ExplanationPersistence:
    """Persists an explanation dict to the database."""

    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        explanation_doc: Dict[str, Any],
        model_version: str,
        algorithm: str,
    ) -> Explanation:
        """Create and commit an Explanation row.

        Parameters
        ----------
        explanation_doc : Canonical explanation dict (from ExplanationReporter.build()).
        model_version   : Registry version string.
        algorithm       : Registry algorithm name.

        Returns
        -------
        Committed Explanation ORM instance.
        """
        try:
            prediction_uuid = UUID(explanation_doc["prediction_id"])
        except (KeyError, ValueError):
            prediction_uuid = None

        try:
            model_uuid = UUID(explanation_doc["model_id"])
        except (KeyError, ValueError):
            model_uuid = None

        row = Explanation(
            prediction_id               = prediction_uuid,
            model_id                    = model_uuid,
            model_version               = model_version,
            algorithm                   = algorithm,
            base_value                  = round(float(explanation_doc["base_value"]), 6),
            feature_names               = explanation_doc["feature_names"],
            shap_values                 = [round(float(v), 6) for v in explanation_doc["shap_values"]],
            feature_importance          = explanation_doc["feature_importance"],
            top_positive_contributors   = explanation_doc["top_positive_contributors"],
            top_negative_contributors   = explanation_doc["top_negative_contributors"],
            prediction_label            = explanation_doc.get("prediction"),
            confidence                  = explanation_doc.get("confidence"),
            warnings                    = explanation_doc.get("warnings", []),
            explained_at                = datetime.now(timezone.utc),
        )

        try:
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
            logger.info(
                "ExplanationPersistence: saved explanation %s for prediction '%s'.",
                row.id, prediction_uuid,
            )
            return row
        except Exception as exc:
            self.db.rollback()
            logger.error("Failed to persist explanation: %s", exc)
            raise
