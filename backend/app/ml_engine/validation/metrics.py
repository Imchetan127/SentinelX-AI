"""MetricsAnalyzer — computes all 18 evaluation metrics.

Produces a fully serialisable dict (no numpy types) so the result can be
stored in JSON columns without additional coercion.
"""
import time
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger("Validation.MetricsAnalyzer")


def _safe_float(value: Any) -> Optional[float]:
    """Cast to Python float; return None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class MetricsAnalyzer:
    """Computes all 18 validation metrics from predictions and ground truth."""

    def compute(
        self,
        model: Any,
        X: pd.DataFrame,
        y_true: pd.Series,
        label_column: str = "Label",
    ) -> Dict[str, Any]:
        """Run full metric suite against *X* / *y_true*.

        Parameters
        ----------
        model     : sklearn-compatible estimator (must implement predict())
        X         : feature DataFrame (already scaled)
        y_true    : ground-truth Series
        label_column : unused but kept for API symmetry

        Returns
        -------
        dict with all 18 metrics; missing values are None (never raises).
        """
        warnings: List[str] = []
        metrics: Dict[str, Any] = {}

        # ── 1. Predictions + latency ──────────────────────────────────────
        t0 = time.perf_counter()
        y_pred = model.predict(X)
        elapsed = time.perf_counter() - t0
        n_samples = max(1, len(X))

        metrics["inference_latency_ms_per_sample"] = round(
            (elapsed * 1000) / n_samples, 5
        )
        metrics["prediction_throughput_per_sec"] = round(
            n_samples / max(elapsed, 1e-9), 2
        )

        # ── 2. Probability outputs (optional) ────────────────────────────
        y_proba: Optional[np.ndarray] = None
        if hasattr(model, "predict_proba"):
            try:
                proba_all = model.predict_proba(X)
                # Binary: take positive-class column
                y_proba = (
                    proba_all[:, 1]
                    if proba_all.ndim == 2 and proba_all.shape[1] == 2
                    else proba_all.max(axis=1)
                )
            except Exception as exc:
                warnings.append(
                    f"predict_proba unavailable — ROC-AUC and Log Loss set to null: {exc}"
                )
                logger.warning("predict_proba failed: %s", exc)

        # ── 3. Core metrics ───────────────────────────────────────────────
        try:
            metrics["accuracy"] = round(float(accuracy_score(y_true, y_pred)), 4)
        except Exception as exc:
            metrics["accuracy"] = None
            warnings.append(f"accuracy calculation failed: {exc}")

        try:
            metrics["balanced_accuracy"] = round(
                float(balanced_accuracy_score(y_true, y_pred)), 4
            )
        except Exception as exc:
            metrics["balanced_accuracy"] = None
            warnings.append(f"balanced_accuracy failed: {exc}")

        try:
            metrics["precision"] = round(
                float(precision_score(y_true, y_pred, zero_division=0, average="binary")), 4
            )
            metrics["precision_macro"] = round(
                float(precision_score(y_true, y_pred, zero_division=0, average="macro")), 4
            )
        except Exception as exc:
            metrics["precision"] = metrics["precision_macro"] = None
            warnings.append(f"precision failed: {exc}")

        try:
            metrics["recall"] = round(
                float(recall_score(y_true, y_pred, zero_division=0, average="binary")), 4
            )
            metrics["recall_macro"] = round(
                float(recall_score(y_true, y_pred, zero_division=0, average="macro")), 4
            )
        except Exception as exc:
            metrics["recall"] = metrics["recall_macro"] = None
            warnings.append(f"recall failed: {exc}")

        # Sensitivity is an alias for recall (binary)
        metrics["sensitivity"] = metrics.get("recall")

        try:
            metrics["f1_score"] = round(
                float(f1_score(y_true, y_pred, zero_division=0, average="binary")), 4
            )
            metrics["f1_score_macro"] = round(
                float(f1_score(y_true, y_pred, zero_division=0, average="macro")), 4
            )
        except Exception as exc:
            metrics["f1_score"] = metrics["f1_score_macro"] = None
            warnings.append(f"f1_score failed: {exc}")

        try:
            metrics["mcc"] = round(float(matthews_corrcoef(y_true, y_pred)), 4)
        except Exception as exc:
            metrics["mcc"] = None
            warnings.append(f"MCC failed: {exc}")

        # ── 4. Probability-dependent metrics ─────────────────────────────
        if y_proba is not None and len(np.unique(y_true)) > 1:
            try:
                metrics["roc_auc"] = round(
                    float(roc_auc_score(y_true, y_proba)), 4
                )
            except Exception as exc:
                metrics["roc_auc"] = None
                warnings.append(f"roc_auc failed: {exc}")

            try:
                metrics["log_loss"] = round(
                    float(log_loss(y_true, y_proba)), 4
                )
            except Exception as exc:
                metrics["log_loss"] = None
                warnings.append(f"log_loss failed: {exc}")
        else:
            metrics["roc_auc"] = None
            metrics["log_loss"] = None
            if y_proba is None:
                warnings.append("roc_auc and log_loss unavailable: predict_proba not supported.")
            else:
                warnings.append(
                    "roc_auc and log_loss unavailable: only one class in y_true."
                )

        # ── 5. Confusion matrix + derived rates ───────────────────────────
        try:
            cm = confusion_matrix(y_true, y_pred)
            metrics["confusion_matrix"] = cm.tolist()

            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
                tn, fp, fn, tp = int(tn), int(fp), int(fn), int(tp)

                metrics["true_negatives"]  = tn
                metrics["false_positives"] = fp
                metrics["false_negatives"] = fn
                metrics["true_positives"]  = tp

                metrics["false_positive_rate"] = round(
                    fp / (fp + tn) if (fp + tn) > 0 else 0.0, 4
                )
                metrics["false_negative_rate"] = round(
                    fn / (fn + tp) if (fn + tp) > 0 else 0.0, 4
                )
                metrics["specificity"] = round(
                    tn / (tn + fp) if (tn + fp) > 0 else 0.0, 4
                )
            else:
                # Multi-class: skip binary-only rates
                for key in ("false_positive_rate", "false_negative_rate", "specificity"):
                    metrics[key] = None
                warnings.append(
                    "FPR/FNR/Specificity not computed for multi-class confusion matrix."
                )
        except Exception as exc:
            metrics["confusion_matrix"] = None
            warnings.append(f"confusion_matrix failed: {exc}")

        # ── 6. Class-wise breakdown ───────────────────────────────────────
        try:
            report = classification_report(
                y_true, y_pred, output_dict=True, zero_division=0
            )
            # Remove non-class aggregates for the class_errors block
            class_report = {
                k: v for k, v in report.items()
                if k not in ("accuracy", "macro avg", "weighted avg")
            }
            metrics["class_report"] = class_report
        except Exception as exc:
            metrics["class_report"] = None
            warnings.append(f"class_report failed: {exc}")

        # ── 7. Support ─────────────────────────────────────────────────────
        metrics["support"] = int(n_samples)

        # ── 8. Confidence distribution ────────────────────────────────────
        if y_proba is not None:
            try:
                metrics["confidence_distribution"] = {
                    "min":    round(float(y_proba.min()), 4),
                    "max":    round(float(y_proba.max()), 4),
                    "mean":   round(float(y_proba.mean()), 4),
                    "std":    round(float(y_proba.std()), 4),
                    "p25":    round(float(np.percentile(y_proba, 25)), 4),
                    "median": round(float(np.percentile(y_proba, 50)), 4),
                    "p75":    round(float(np.percentile(y_proba, 75)), 4),
                }
            except Exception as exc:
                metrics["confidence_distribution"] = None
                warnings.append(f"confidence_distribution failed: {exc}")
        else:
            metrics["confidence_distribution"] = None

        metrics["warnings"] = warnings
        logger.info(
            "MetricsAnalyzer complete. accuracy=%.4f, f1=%.4f, support=%d",
            metrics.get("accuracy") or 0,
            metrics.get("f1_score") or 0,
            metrics["support"],
        )
        return metrics
