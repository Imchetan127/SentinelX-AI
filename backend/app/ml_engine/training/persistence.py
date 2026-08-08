import os
import joblib
import logging
from typing import Any

logger = logging.getLogger("ModelTraining.Persistence")


class PersistenceService:
    def __init__(self, base_dir: str = "../models"):
        self.base_dir = base_dir
        self.artifacts_dir = os.path.join(base_dir, "artifacts")
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def save_model(self, model: Any, filename: str) -> str:
        filepath = os.path.join(self.artifacts_dir, filename)
        
        # 1. Enforce that it never overwrites existing model versions
        if os.path.exists(filepath):
            error_msg = f"Model artifact version conflict: File already exists at: {filepath}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Saving model artifact to: {filepath}")
        try:
            joblib.dump(model, filepath)
        except Exception as e:
            error_msg = f"Failed to serialize model artifact: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        return filepath

    def load_model(self, filename: str) -> Any:
        filepath = os.path.join(self.artifacts_dir, filename)
        if not os.path.exists(filepath):
            error_msg = f"Model artifact not found at: {filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading model artifact from: {filepath}")
        try:
            model = joblib.load(filepath)
        except Exception as e:
            error_msg = f"Failed to deserialize model artifact: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        return model
