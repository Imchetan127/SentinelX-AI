"""ExplanationReporter — assembles the canonical structured explanation object.

Pure function-like component; receives all sub-results and builds a
fully serialisable explanation dict. No DB writes, no service calls.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

logger = logging.getLogger("Explainability.Reporter")

REQUIRED_EXPLANATION_FIELDS = {
    "explanation_id",
    "prediction_id",
    "model_id",
    "model_version",
    "algorithm",
    "prediction",
    "confidence",
    "base_value",
    "shap_values",
    "feature_names",
    "feature_importance",
    "top_positive_contributors",
    "top_negative_contributors",
    "warnings",
    "explained_at",
}


class ExplanationReporter:
    """Assembles structured explanation documents from SHAPEngine output."""

    def build(
        self,
        prediction_id:  UUID,
        model_id:       UUID,
        model_version:  str,
        algorithm:      str,
        prediction:     str,
        confidence:     float,
        shap_output:    Dict[str, Any],
        extra_warnings: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Build and return the canonical explanation document.

        Parameters
        ----------
        prediction_id  : UUID of the originating prediction.
        model_id       : UUID of the model that produced the prediction.
        model_version  : Version string from the registry.
        algorithm      : Algorithm name from the registry.
        prediction     : Prediction label ("malicious" / "clean").
        confidence     : Prediction confidence score [0, 1].
        shap_output    : Dict from SHAPEngine.explain().
        extra_warnings : Additional warnings from the orchestrator.
        """
        now = datetime.now(timezone.utc).isoformat()

        # Merge all warnings
        shap_warnings  = shap_output.get("warnings", [])
        all_warnings   = list(shap_warnings) + list(extra_warnings or [])

        explanation: Dict[str, Any] = {
            "explanation_id":           str(uuid4()),
            "prediction_id":            str(prediction_id),
            "model_id":                 str(model_id),
            "model_version":            model_version,
            "algorithm":                algorithm,
            "prediction":               prediction,
            "confidence":               round(float(confidence), 4),
            "base_value":               shap_output["base_value"],
            "shap_values":              shap_output["shap_values"],
            "feature_names":            shap_output["feature_names"],
            "feature_importance":       shap_output["feature_importance"],
            "top_positive_contributors": shap_output["top_positive_contributors"],
            "top_negative_contributors": shap_output["top_negative_contributors"],
            "warnings":                 all_warnings,
            "explained_at":             now,
        }

        logger.info(
            "ExplanationReporter: built explanation for prediction '%s'. "
            "algorithm=%s, top_positive=%s.",
            prediction_id, algorithm,
            [c["feature"] for c in explanation["top_positive_contributors"]],
        )
        return explanation
