import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

logger = logging.getLogger("ModelTraining.Evaluation")


class EvaluationService:
    def __init__(self):
        pass

    def evaluate(self, model: Any, X_val: pd.DataFrame, y_val: pd.Series, training_duration_sec: float) -> Dict[str, Any]:
        logger.info("Starting model evaluation process...")

        # 1. Measure prediction time
        t0 = time.perf_counter()
        y_pred = model.predict(X_val)
        prediction_duration_sec = time.perf_counter() - t0
        
        # Prediction time per sample in milliseconds
        prediction_time_per_sample_ms = (prediction_duration_sec * 1000) / max(1, len(X_val))

        # Check if probabilities can be generated for ROC-AUC
        y_proba = None
        roc_auc = 0.0
        if hasattr(model, "predict_proba"):
            try:
                y_proba = model.predict_proba(X_val)[:, 1]
                if len(np.unique(y_val)) > 1:
                    roc_auc = float(roc_auc_score(y_val, y_proba))
                else:
                    logger.warning("ROC-AUC calculation skipped: only one unique target class present in validation set.")
                    roc_auc = 1.0 if list(y_val)[0] == list(y_pred)[0] else 0.0
            except Exception as e:
                logger.warning(f"Failed to calculate ROC-AUC using predict_proba: {str(e)}")

        # 2. Compute metrics
        accuracy = float(accuracy_score(y_val, y_pred))
        precision = float(precision_score(y_val, y_pred, zero_division=0))
        recall = float(recall_score(y_val, y_pred, zero_division=0))
        f1 = float(f1_score(y_val, y_pred, zero_division=0))

        # 3. Compute Confusion Matrix
        cm = confusion_matrix(y_val, y_pred)
        confusion_matrix_list = cm.tolist()  # Convert numpy array to JSON serializable list of lists

        # 4. Class Distribution & Support
        class_counts = y_val.value_counts(dropna=False)
        class_distribution = {str(k): int(v) for k, v in class_counts.items()}

        metrics = {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": confusion_matrix_list,
            "training_time_sec": round(training_duration_sec, 3),
            "prediction_time_val_sec": round(prediction_duration_sec, 4),
            "prediction_time_per_sample_ms": round(prediction_time_per_sample_ms, 5),
            "class_distribution": class_distribution,
            "support": int(len(y_val))
        }

        logger.info(f"Model evaluation completed. Metrics: {metrics}")
        return metrics
