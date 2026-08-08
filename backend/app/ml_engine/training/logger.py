import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("ModelTraining.Logger")


class ExperimentLogger:
    def __init__(self, base_dir: str = "../models"):
        self.base_dir = base_dir
        self.metadata_dir = os.path.join(base_dir, "metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

    def log_experiment(
        self,
        algorithm: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        dataset_hash: str,
        pipeline_version: str,
        model_version: str,
        training_duration_sec: float,
        validation_duration_sec: float
    ) -> str:
        timestamp_str = datetime.now(timezone.utc).isoformat()
        experiment_id = f"exp_{algorithm.lower()}_{model_version}_{int(datetime.now(timezone.utc).timestamp())}"
        
        experiment_record = {
            "experiment_id": experiment_id,
            "timestamp": timestamp_str,
            "algorithm": algorithm.lower(),
            "model_version": model_version,
            "pipeline_version": pipeline_version,
            "dataset_hash": dataset_hash,
            "hyperparameters": hyperparameters,
            "metrics": metrics,
            "durations": {
                "training_sec": round(training_duration_sec, 3),
                "validation_sec": round(validation_duration_sec, 4)
            }
        }

        meta_filepath = os.path.join(self.metadata_dir, f"{experiment_id}.json")
        logger.info(f"Logging experiment run record to: {meta_filepath}")
        
        try:
            with open(meta_filepath, "w") as f:
                json.dump(experiment_record, f, indent=4)
        except Exception as e:
            error_msg = f"Failed to write experiment run metadata: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        return meta_filepath
