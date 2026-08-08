"""CrossValidator — stratified k-fold cross-validation.

Runs configurable k-fold stratified cross-validation on the combined
train+val split and returns per-fold scores plus mean, std, and 95% CI.
"""
import logging
import math
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, roc_auc_score

logger = logging.getLogger("Validation.CrossValidator")

_DEFAULT_SCORING = {
    "accuracy":  "accuracy",
    "precision": "precision",
    "recall":    "recall",
    "f1_score":  "f1",
    "balanced_accuracy": "balanced_accuracy",
}


def _try_add_roc_auc(model: Any, scoring: dict) -> dict:
    """Add roc_auc scorer only if the model supports predict_proba."""
    if hasattr(model, "predict_proba"):
        scoring = dict(scoring)
        scoring["roc_auc"] = "roc_auc"
    return scoring


class CrossValidator:
    """Stratified K-Fold cross-validation with CI reporting."""

    def __init__(
        self,
        n_folds: int = 5,
        random_state: int = 42,
        scoring: Optional[Dict[str, str]] = None,
    ):
        self.n_folds = n_folds
        self.random_state = random_state
        self.scoring = scoring or _DEFAULT_SCORING

    def run(
        self,
        model: Any,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> Dict[str, Any]:
        """Run stratified k-fold CV on the combined train+val split.

        Returns
        -------
        {
          "n_folds":   int,
          "results":   {metric: {"mean", "std", "ci_lower", "ci_upper", "fold_scores"}},
          "warnings":  [str]
        }
        """
        warnings: List[str] = []

        # Combine train and val into a single pool for CV
        X_cv = pd.concat([X_train, X_val], ignore_index=True)
        y_cv = pd.concat([y_train, y_val], ignore_index=True)

        scoring = _try_add_roc_auc(model, self.scoring)

        skf = StratifiedKFold(
            n_splits=self.n_folds,
            shuffle=True,
            random_state=self.random_state,
        )

        try:
            cv_raw = cross_validate(
                model,
                X_cv,
                y_cv,
                cv=skf,
                scoring=scoring,
                return_train_score=False,
                error_score="raise",
            )
        except Exception as exc:
            logger.warning("Cross-validation failed: %s", exc)
            warnings.append(f"Cross-validation failed — results omitted: {exc}")
            return {
                "n_folds": self.n_folds,
                "results": {},
                "warnings": warnings,
            }

        results: Dict[str, Any] = {}
        for metric_key, scorer_name in scoring.items():
            raw_key = f"test_{metric_key}"
            if raw_key not in cv_raw:
                warnings.append(f"CV score key '{raw_key}' not found in results.")
                continue

            fold_scores = [round(float(s), 4) for s in cv_raw[raw_key]]
            mean_val = float(np.mean(fold_scores))
            std_val  = float(np.std(fold_scores, ddof=1)) if len(fold_scores) > 1 else 0.0
            # 95% CI: mean ± 1.96 * (std / sqrt(k))
            margin = 1.96 * (std_val / math.sqrt(self.n_folds))

            results[metric_key] = {
                "mean":       round(mean_val, 4),
                "std":        round(std_val, 4),
                "ci_lower":   round(mean_val - margin, 4),
                "ci_upper":   round(mean_val + margin, 4),
                "fold_scores": fold_scores,
            }

        logger.info(
            "CrossValidator complete. %d folds. accuracy_mean=%.4f ± %.4f",
            self.n_folds,
            results.get("accuracy", {}).get("mean", 0),
            results.get("accuracy", {}).get("std", 0),
        )
        return {
            "n_folds":  self.n_folds,
            "results":  results,
            "warnings": warnings,
        }
