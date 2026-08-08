"""ThresholdEvaluator + QualityGate — configurable production promotion gates.

ThresholdEvaluator
------------------
Evaluates a metrics dict against a set of configurable thresholds.
Returns a structured list of per-threshold pass/fail results.

QualityGate
-----------
Wraps ThresholdEvaluator and produces the final PASSED / FAILED verdict
with a human-readable list of reasons for every failed threshold.

The gate decision is advisory only. Governance is responsible for
actual lifecycle transitions.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Validation.ThresholdEvaluator")

# Default PRODUCTION quality gate thresholds
DEFAULT_THRESHOLDS: Dict[str, float] = {
    "accuracy":  0.90,
    "precision": 0.90,
    "recall":    0.85,
    "f1_score":  0.88,
    "roc_auc":   0.92,
}


@dataclass
class ThresholdResult:
    """Result for a single threshold evaluation."""
    metric:    str
    threshold: float
    value:     Optional[float]   # None when the metric was not computed
    passed:    bool
    reason:    Optional[str] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric":    self.metric,
            "threshold": self.threshold,
            "value":     self.value,
            "passed":    self.passed,
            "reason":    self.reason,
        }


class ThresholdEvaluator:
    """Evaluates a metrics dict against configurable minimum thresholds."""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS

    def evaluate(self, metrics: Dict[str, Any]) -> List[ThresholdResult]:
        """Return a list of ThresholdResult — one entry per configured threshold."""
        results: List[ThresholdResult] = []

        for metric_key, min_value in self.thresholds.items():
            raw = metrics.get(metric_key)

            if raw is None:
                # Metric not available (e.g., roc_auc when predict_proba absent)
                result = ThresholdResult(
                    metric=metric_key,
                    threshold=min_value,
                    value=None,
                    passed=False,
                    reason=(
                        f"'{metric_key}' could not be computed (metric not available). "
                        f"Required: ≥ {min_value}."
                    ),
                )
            else:
                actual = float(raw)
                passed = actual >= min_value
                result = ThresholdResult(
                    metric=metric_key,
                    threshold=min_value,
                    value=round(actual, 4),
                    passed=passed,
                    reason=(
                        None
                        if passed
                        else (
                            f"'{metric_key}' is {actual:.4f} — below minimum "
                            f"threshold of {min_value}."
                        )
                    ),
                )

            results.append(result)
            logger.debug(
                "Threshold '%s': value=%s, threshold=%s, passed=%s",
                metric_key, raw, min_value, result.passed
            )

        return results


class QualityGate:
    """Combines threshold evaluation into a single PASSED / FAILED verdict."""

    RESULT_PASSED = "PASSED"
    RESULT_FAILED = "FAILED"

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.evaluator = ThresholdEvaluator(thresholds=thresholds)

    def evaluate(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Return the quality gate verdict dict.

        Returns
        -------
        {
          "result":           "PASSED" | "FAILED",
          "threshold_results": [ThresholdResult.to_dict(), ...],
          "reasons":          [str, ...]   # non-empty only when FAILED
        }
        """
        threshold_results = self.evaluator.evaluate(metrics)
        failures = [r for r in threshold_results if not r.passed]
        reasons  = [r.reason for r in failures if r.reason]
        result   = self.RESULT_PASSED if not failures else self.RESULT_FAILED

        logger.info(
            "QualityGate verdict: %s (%d/%d thresholds passed).",
            result,
            len(threshold_results) - len(failures),
            len(threshold_results),
        )

        return {
            "result":            result,
            "threshold_results": [r.to_dict() for r in threshold_results],
            "reasons":           reasons,
        }
