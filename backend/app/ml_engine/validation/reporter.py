"""ValidationReporter — assembles the canonical structured validation report.

The reporter is a pure function-like component: it receives all computed
sub-results and assembles them into a single serialisable report dict.
It does not write to the database or call any services.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger("Validation.Reporter")

VALIDATOR_VERSION = "1.0.0"

REQUIRED_REPORT_FIELDS = {
    "report_id", "model_id", "algorithm", "version",
    "dataset_version", "pipeline_version", "validator_version",
    "validated_at", "metrics", "cross_validation",
    "threshold_results", "quality_gate", "error_analysis",
    "warnings", "limitations", "recommendation",
}


class ValidationReporter:
    """Assembles structured validation reports from sub-component outputs."""

    def build_report(
        self,
        model_meta:       Dict[str, Any],
        metrics:          Dict[str, Any],
        cv_results:       Dict[str, Any],
        quality_gate:     Dict[str, Any],
        extra_warnings:   Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Assemble and return the canonical validation report.

        Parameters
        ----------
        model_meta    : Registry entry for the model under test.
        metrics       : Output of MetricsAnalyzer.compute().
        cv_results    : Output of CrossValidator.run().
        quality_gate  : Output of QualityGate.evaluate().
        extra_warnings: Additional warnings from the orchestrator.
        """
        now = datetime.now(timezone.utc).isoformat()
        model_id  = model_meta.get("model_id", "unknown")
        algorithm = model_meta.get("algorithm", "unknown")
        version   = model_meta.get("version",   "unknown")

        # Merge all warning sources
        metric_warnings = metrics.pop("warnings", []) if isinstance(metrics, dict) else []
        cv_warnings     = cv_results.get("warnings", [])
        all_warnings: List[str] = list(metric_warnings) + list(cv_warnings) + list(extra_warnings or [])

        # Error analysis block (extracted from metrics for clarity)
        error_analysis = _build_error_analysis(metrics)

        # Determine recommendation text
        gate_result  = quality_gate.get("result", "FAILED")
        gate_reasons = quality_gate.get("reasons", [])
        recommendation = _build_recommendation(gate_result, gate_reasons, algorithm, version)

        report: Dict[str, Any] = {
            "report_id":        str(uuid4()),
            "model_id":         model_id,
            "algorithm":        algorithm,
            "version":          version,
            "dataset_version":  model_meta.get("dataset_version", "unknown"),
            "pipeline_version": model_meta.get("preprocessing_version", "unknown"),
            "validator_version": VALIDATOR_VERSION,
            "validated_at":     now,

            # Full metrics dict (18 metrics)
            "metrics": _strip_internal(metrics),

            # Cross-validation summary
            "cross_validation": {
                "n_folds": cv_results.get("n_folds", 0),
                "results": cv_results.get("results", {}),
            },

            # Threshold gate
            "threshold_results": quality_gate.get("threshold_results", []),
            "quality_gate": {
                "result":  gate_result,
                "reasons": gate_reasons,
            },

            # Error analysis section
            "error_analysis": error_analysis,

            # Non-fatal warnings
            "warnings": all_warnings,

            # Limitations (static; can be extended from registry metadata)
            "limitations": (
                model_meta.get("known_limitations")
                or "Evaluated on the held-out test split of the training dataset. "
                   "Performance on unseen production traffic may vary."
            ),

            # Recommendation (objective, based on gate result)
            "recommendation": recommendation,

            # Provenance
            "timestamp": now,
        }

        logger.info(
            "ValidationReporter: report assembled for model '%s' v%s. Gate=%s.",
            algorithm, version, gate_result
        )
        return report


def _build_error_analysis(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Extract error-focused metrics into a dedicated section."""
    return {
        "false_positives":  metrics.get("false_positives"),
        "false_negatives":  metrics.get("false_negatives"),
        "true_positives":   metrics.get("true_positives"),
        "true_negatives":   metrics.get("true_negatives"),
        "false_positive_rate": metrics.get("false_positive_rate"),
        "false_negative_rate": metrics.get("false_negative_rate"),
        "class_errors":     metrics.get("class_report"),
        "confidence_distribution": metrics.get("confidence_distribution"),
    }


def _build_recommendation(
    gate_result: str,
    reasons: List[str],
    algorithm: str,
    version: str,
) -> str:
    if gate_result == "PASSED":
        return (
            f"Model {algorithm} v{version} meets all configured quality gate thresholds. "
            "It is eligible for PRODUCTION promotion via the Model Governance service."
        )
    reason_list = "; ".join(reasons) if reasons else "one or more thresholds not met"
    return (
        f"Model {algorithm} v{version} did NOT meet all quality gate thresholds. "
        f"Reason(s): {reason_list}. "
        "Model should not be promoted to PRODUCTION until deficiencies are addressed."
    )


def _strip_internal(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Remove internal tracking keys before embedding in the report."""
    drop = {"warnings"}
    return {k: v for k, v in metrics.items() if k not in drop}
