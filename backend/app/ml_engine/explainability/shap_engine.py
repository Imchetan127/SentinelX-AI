"""SHAPEngine — deterministic SHAP computation using TreeExplainer.

Responsibilities
----------------
- Select the correct SHAP explainer class based on the model algorithm.
- Compute SHAP values for a single scaled feature row.
- Normalise output (handle binary RF list-of-arrays vs XGBoost single array).
- Return a structured dict ready for ExplanationValidator and ExplanationReporter.

Does NOT touch the database, registry, or audit trail.
"""
import logging
import math
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("Explainability.SHAPEngine")

# Algorithms supported by TreeExplainer
_TREE_ALGORITHMS = frozenset({
    "random_forest", "randomforest",
    "xgboost", "xgb",
})


class UnsupportedModelError(ValueError):
    """Raised when the requested model algorithm has no SHAP explainer support."""
    supported_types = sorted(_TREE_ALGORITHMS)


class SHAPEngine:
    """Computes SHAP feature-contribution values using the model-specific explainer."""

    def __init__(self, top_n: int = 5):
        """
        Parameters
        ----------
        top_n : int
            Number of top positive and top negative contributors to surface.
        """
        self.top_n = top_n

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def explain(
        self,
        model: Any,
        algorithm: str,
        X_scaled: pd.DataFrame,
        feature_names: List[str],
    ) -> Dict[str, Any]:
        """Compute SHAP explanation for a single row in *X_scaled*.

        Parameters
        ----------
        model        : fitted sklearn / XGBoost estimator
        algorithm    : lowercase algorithm name from the registry
        X_scaled     : single-row DataFrame (already preprocessed)
        feature_names: ordered list of feature column names

        Returns
        -------
        {
          "base_value"  : float,
          "shap_values" : list[float],   # one value per feature
          "feature_names": list[str],
          "feature_importance": list[{feature, shap_value, direction}],
          "top_positive_contributors": list[{feature, shap_value}],
          "top_negative_contributors": list[{feature, shap_value}],
          "warnings": list[str],
        }
        """
        alg = algorithm.lower().strip()
        warnings: List[str] = []

        if alg not in _TREE_ALGORITHMS:
            raise UnsupportedModelError(
                f"Model algorithm '{algorithm}' is not supported for XAI. "
                f"Supported algorithms: {sorted(_TREE_ALGORITHMS)}."
            )

        # ── Build explainer ───────────────────────────────────────────
        try:
            import shap
            explainer = shap.TreeExplainer(model)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialise TreeExplainer for '{algorithm}': {exc}"
            ) from exc

        # ── Compute SHAP values ───────────────────────────────────────
        try:
            raw_shap = explainer.shap_values(X_scaled)
        except Exception as exc:
            raise RuntimeError(
                f"SHAP value computation failed for '{algorithm}': {exc}"
            ) from exc

        base_val = explainer.expected_value

        # ── Normalise output shape ────────────────────────────────────
        # Binary Random Forest: shap_values is list of 2 arrays [class0, class1].
        # XGBoost: single 2D array of shape (n_samples, n_features).
        shap_row = _extract_row_shap(raw_shap, base_val, alg)
        base_value = _extract_base_value(base_val, alg)

        n_feats = len(feature_names)
        if len(shap_row) != n_feats:
            warnings.append(
                f"SHAP value count ({len(shap_row)}) differs from "
                f"feature count ({n_feats}). Values may be misaligned."
            )

        shap_floats = [float(v) for v in shap_row]

        # ── Build feature importance table ─────────────────────────────
        importance = _build_importance(feature_names, shap_floats)

        top_positive = [
            {"feature": e["feature"], "shap_value": e["shap_value"]}
            for e in importance
            if e["shap_value"] > 0
        ][: self.top_n]

        top_negative = [
            {"feature": e["feature"], "shap_value": e["shap_value"]}
            for e in importance
            if e["shap_value"] < 0
        ][: self.top_n]

        logger.info(
            "SHAPEngine: explained '%s'. base_value=%.4f. "
            "top_positive=%s top_negative=%s.",
            algorithm, base_value,
            [c["feature"] for c in top_positive],
            [c["feature"] for c in top_negative],
        )

        return {
            "base_value":               base_value,
            "shap_values":              shap_floats,
            "feature_names":            list(feature_names),
            "feature_importance":       importance,
            "top_positive_contributors": top_positive,
            "top_negative_contributors": top_negative,
            "warnings":                 warnings,
        }


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _extract_row_shap(raw_shap: Any, base_val: Any, alg: str) -> np.ndarray:
    """Return a 1-D numpy float64 array of SHAP values for the single input row.

    Handles all output shapes produced by SHAP TreeExplainer:
      - list of 2 arrays  (binary RF, old SHAP API)       → use index [1]
      - 3-D (n_samples, n_features, n_classes)            (newer SHAP RF) → [0, :, -1]
      - 3-D (n_classes, n_samples, n_features)            (alt layout)    → [-1, 0]
      - 2-D (n_samples, n_features)                       (XGBoost)       → [0]
      - 1-D (n_features)                                  (single sample) → as-is
    """
    if isinstance(raw_shap, list):
        arr = np.asarray(raw_shap[1], dtype=np.float64)
        return arr[0] if arr.ndim == 2 else arr.flatten()

    arr = np.asarray(raw_shap, dtype=np.float64)
    if arr.ndim == 3:
        # Distinguish (n_samples, n_features, n_classes) from (n_classes, n_samples, n_features)
        # by checking whether the first axis size == 1 (single sample was passed).
        if arr.shape[0] == 1:
            # (1, n_features, n_classes) — take the positive/last class column
            return arr[0, :, -1]
        else:
            # (n_classes, n_samples, n_features)
            return arr[-1, 0]
    if arr.ndim == 2:
        return arr[0]
    return arr.flatten()


def _extract_base_value(base_val: Any, alg: str) -> float:
    """Coerce expected_value to a single float (handles ndarray/list)."""
    if isinstance(base_val, (list, np.ndarray)):
        b = np.asarray(base_val)
        # Binary RF: two expected values; use the positive class
        return round(float(b[1] if len(b) > 1 else b[0]), 6)
    return round(float(base_val), 6)


def _build_importance(
    feature_names: List[str],
    shap_floats: List[float],
) -> List[Dict[str, Any]]:
    """Return importance list sorted by absolute SHAP value descending."""
    rows = [
        {
            "feature":    feature_names[i],
            "shap_value": shap_floats[i],
            "direction":  "positive" if shap_floats[i] >= 0 else "negative",
        }
        for i in range(len(feature_names))
    ]
    return sorted(rows, key=lambda x: abs(x["shap_value"]), reverse=True)
