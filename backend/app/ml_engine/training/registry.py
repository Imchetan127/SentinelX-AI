import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

logger = logging.getLogger("ModelTraining.Registry")


class ModelRegistry:
    def __init__(self, base_dir: str = "../models"):
        self.base_dir = base_dir
        self.registry_dir = os.path.join(base_dir, "registry")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_filepath = os.path.join(self.registry_dir, "registry.json")
        self._load_registry()

    def _load_registry(self) -> None:
        if os.path.exists(self.registry_filepath):
            try:
                with open(self.registry_filepath, "r") as f:
                    self.registry_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load model registry database: {str(e)}. Corrupt file.")
                # We raise an error for corrupt registry as required in Error Handling
                raise RuntimeError(f"Corrupted registry database: {str(e)}")
        else:
            self.registry_data = []
            self._save_registry()

    def _save_registry(self) -> None:
        try:
            with open(self.registry_filepath, "w") as f:
                json.dump(self.registry_data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save model registry database: {str(e)}")
            raise RuntimeError(f"Failed model registry database write: {str(e)}")

    def register_model(
        self,
        algorithm: str,
        version: str,
        dataset_version: str,
        preprocessing_version: str,
        metrics: Dict[str, Any],
        hyperparameters: Dict[str, Any],
        storage_path: str,
        status: str = "VALIDATED",
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Generate model metadata details
        m_id = model_id or str(uuid.uuid4())

        # Ensure model version does not duplicate an existing algorithm's version
        for entry in self.registry_data:
            if entry["algorithm"].lower() == algorithm.lower() and entry["version"] == version:
                error_msg = f"Version conflict: Algorithm '{algorithm}' version '{version}' is already registered."
                logger.error(error_msg)
                raise ValueError(error_msg)

        metadata = {
            "model_id": m_id,
            "version": version,
            "algorithm": algorithm.lower(),
            "dataset_version": dataset_version,
            "preprocessing_version": preprocessing_version,
            "training_timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "hyperparameters": hyperparameters,
            "status": status,
            "storage_path": storage_path
        }

        # 2. Append to registry database
        self.registry_data.append(metadata)
        self._save_registry()

        # 3. Save model specific metadata file as backup
        individual_meta_path = os.path.join(self.registry_dir, f"{algorithm.lower()}_{version}_metadata.json")
        try:
            with open(individual_meta_path, "w") as f:
                json.dump(metadata, f, indent=4)
        except Exception as e:
            logger.warning(f"Failed to save individual model metadata backup: {str(e)}")

        logger.info(f"Model successfully registered under ID {m_id}. Version: {version}.")
        return metadata

    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        for entry in self.registry_data:
            if entry["model_id"] == model_id:
                return entry
        return None

    def list_models(self) -> List[Dict[str, Any]]:
        return self.registry_data
