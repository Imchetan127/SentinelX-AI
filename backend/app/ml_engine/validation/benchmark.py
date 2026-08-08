"""BenchmarkEngine — per-model evaluation coordinator.

Orchestrates:
  1. Loading model artifact + dataset splits via ModelLoader.
  2. Computing all 18 metrics via MetricsAnalyzer.
  3. Running stratified k-fold cross-validation via CrossValidator.
  4. Evaluating quality gate thresholds via QualityGate.
  5. Assembling the full report via ValidationReporter.

Does NOT write to the database — that is the responsibility of ValidationService.
"""
import logging
from typing import Any, Dict, List, Optional

from app.ml_engine.validation.loader import ModelLoader
from app.ml_engine.validation.metrics import MetricsAnalyzer
from app.ml_engine.validation.cross_validator import CrossValidator
from app.ml_engine.validation.threshold import QualityGate, DEFAULT_THRESHOLDS
from app.ml_engine.validation.reporter import ValidationReporter

logger = logging.getLogger("Validation.BenchmarkEngine")


class BenchmarkEngine:
    """Runs the full validation pipeline for a single model."""

    def __init__(
        self,
        base_dir:       str = "../models",
        datasets_dir:   str = "../datasets",
        n_folds:        int = 5,
        thresholds:     Optional[Dict[str, float]] = None,
        label_column:   str = "Label",
    ):
        self.loader      = ModelLoader(base_dir=base_dir, datasets_dir=datasets_dir)
        self.metrics     = MetricsAnalyzer()
        self.cv          = CrossValidator(n_folds=n_folds)
        self.gate        = QualityGate(thresholds=thresholds or DEFAULT_THRESHOLDS)
        self.reporter    = ValidationReporter()
        self.label_column = label_column

    def validate_model(
        self,
        model_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run full validation for a single registry entry.

        Returns
        -------
        {
          model_id, algorithm, version, status,
          metrics, cv_results, quality_gate,
          report, warnings, error
        }
        "error" key is set (non-None) when validation fails completely.
        """
        model_id  = model_meta.get("model_id", "?")
        algorithm = model_meta.get("algorithm", "?")
        version   = model_meta.get("version", "?")
        warnings: List[str] = []

        logger.info(
            "BenchmarkEngine: validating model '%s' v%s (ID: %s)",
            algorithm, version, model_id
        )

        # ── 1. Load artifact and splits ───────────────────────────────────
        try:
            payload = self.loader.load_for_validation(model_meta, self.label_column)
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            logger.error("Model load failed for '%s' v%s: %s", algorithm, version, exc)
            return _error_result(model_meta, str(exc))

        model  = payload["model"]
        splits = payload["splits"]
        X_train, y_train = splits["train"]
        X_val,   y_val   = splits["val"]
        X_test,  y_test  = splits["test"]

        # ── 2. Hold-out test-set metrics ──────────────────────────────────
        try:
            test_metrics = self.metrics.compute(
                model=model, X=X_test, y_true=y_test,
                label_column=self.label_column
            )
        except Exception as exc:
            logger.error("Metric computation failed: %s", exc)
            return _error_result(model_meta, f"Metrics computation failed: {exc}")

        # Collect metric-level warnings
        warnings.extend(test_metrics.get("warnings", []))

        # ── 3. Cross-validation ───────────────────────────────────────────
        try:
            cv_results = self.cv.run(
                model=model,
                X_train=X_train, y_train=y_train,
                X_val=X_val,     y_val=y_val,
            )
        except Exception as exc:
            logger.warning("Cross-validation failed (non-fatal): %s", exc)
            cv_results = {"n_folds": self.cv.n_folds, "results": {}, "warnings": [str(exc)]}
            warnings.append(f"Cross-validation failed: {exc}")

        # ── 4. Quality gate ───────────────────────────────────────────────
        try:
            quality_gate = self.gate.evaluate(test_metrics)
        except Exception as exc:
            logger.error("Quality gate evaluation failed: %s", exc)
            return _error_result(model_meta, f"Quality gate failed: {exc}")

        # ── 5. Assemble report ────────────────────────────────────────────
        try:
            report = self.reporter.build_report(
                model_meta=model_meta,
                metrics=dict(test_metrics),   # pass a copy; reporter may mutate
                cv_results=cv_results,
                quality_gate=quality_gate,
                extra_warnings=warnings,
            )
        except Exception as exc:
            logger.error("Report assembly failed: %s", exc)
            return _error_result(model_meta, f"Report assembly failed: {exc}")

        # Strip internal warning key from final metrics (already in report)
        final_metrics = {k: v for k, v in test_metrics.items() if k != "warnings"}

        return {
            "model_id":    model_id,
            "algorithm":   algorithm,
            "version":     version,
            "status":      model_meta.get("status"),
            "metrics":     final_metrics,
            "cv_results":  cv_results,
            "quality_gate": quality_gate,
            "report":      report,
            "warnings":    warnings,
            "error":       None,
        }


def _error_result(model_meta: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
    """Return a structured failure result dict."""
    return {
        "model_id":    model_meta.get("model_id"),
        "algorithm":   model_meta.get("algorithm"),
        "version":     model_meta.get("version"),
        "status":      model_meta.get("status"),
        "metrics":     None,
        "cv_results":  None,
        "quality_gate": {"result": "FAILED", "reasons": [error_msg], "threshold_results": []},
        "report":      None,
        "warnings":    [error_msg],
        "error":       error_msg,
    }
