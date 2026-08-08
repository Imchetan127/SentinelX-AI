import os
import json
import time
import logging
import pandas as pd
from typing import Dict, Any, List

from app.ml_engine.training.persistence import PersistenceService
from app.ml_engine.training.evaluation import EvaluationService
from app.ml_engine.training.registry import ModelRegistry
from app.ml_engine.training.logger import ExperimentLogger
from app.ml_engine.training.trainer import ModelTrainer

logger = logging.getLogger("ModelTraining.Pipeline")


class TrainingService:
    def __init__(self, base_dir: str = "../models", datasets_dir: str = "../datasets"):
        self.base_dir = base_dir
        self.datasets_dir = datasets_dir
        
        # Initialize subcomponents
        self.persistence = PersistenceService(base_dir=base_dir)
        self.evaluation = EvaluationService()
        self.registry = ModelRegistry(base_dir=base_dir)
        self.exp_logger = ExperimentLogger(base_dir=base_dir)
        self.trainer = ModelTrainer()

    def load_processed_splits(
        self,
        dataset_name: str,
        dataset_version: str,
        label_column: str = "Label"
    ) -> Dict[str, Any]:
        logger.info(f"Loading processed dataset splits: {dataset_name} v{dataset_version}")
        
        processed_dir = os.path.join(self.datasets_dir, "processed")
        train_path = os.path.join(processed_dir, f"{dataset_name}_{dataset_version}_train.csv")
        val_path = os.path.join(processed_dir, f"{dataset_name}_{dataset_version}_val.csv")
        test_path = os.path.join(processed_dir, f"{dataset_name}_{dataset_version}_test.csv")

        # Gracefully handle missing processed dataset
        for path in [train_path, val_path, test_path]:
            if not os.path.exists(path):
                error_msg = f"Processed dataset split file missing at: {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        try:
            df_train = pd.read_csv(train_path)
            df_val = pd.read_csv(val_path)
            df_test = pd.read_csv(test_path)
        except Exception as e:
            error_msg = f"Failed to load processed split files: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Separate feature and target
        def split_xy(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
            if label_column not in df.columns:
                raise ValueError(f"Label column '{label_column}' not found in loaded splits.")
            X = df.drop(columns=[label_column])
            y = df[label_column]
            return X, y

        from typing import Tuple
        X_train, y_train = split_xy(df_train)
        X_val, y_val = split_xy(df_val)
        X_test, y_test = split_xy(df_test)

        # Get dataset hash if metadata file exists
        dataset_hash = "unknown"
        metadata_path = os.path.join(self.datasets_dir, "metadata", f"{dataset_name}_{dataset_version}_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    meta_data = json.load(f)
                    dataset_hash = meta_data.get("file_hashes", {}).get("train", "unknown")
            except Exception:
                pass

        return {
            "splits": {
                "train": (X_train, y_train),
                "val": (X_val, y_val),
                "test": (X_test, y_test)
            },
            "dataset_hash": dataset_hash
        }

    def run_training_experiment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        algorithm = config.get("algorithm")
        if not algorithm:
            raise ValueError("Configuration must contain 'algorithm' parameter.")

        random_seed = config.get("random_seed", 42)
        hyperparameters = config.get("hyperparameters", {})
        dataset_name = config.get("dataset_name", "default_dataset")
        dataset_version = config.get("dataset_version", "v1")
        preprocessing_version = config.get("preprocessing_version", "p1")
        model_version = config.get("model_version", "1.0.0")
        label_column = config.get("label_column", "Label")

        # 1. Load splits
        data_data = self.load_processed_splits(
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            label_column=label_column
        )
        splits = data_data["splits"]
        dataset_hash = data_data["dataset_hash"]
        X_train, y_train = splits["train"]
        X_val, y_val = splits["val"]

        # 2. Train model
        model, train_duration = self.trainer.train(
            algorithm=algorithm,
            X_train=X_train,
            y_train=y_train,
            hyperparameters=hyperparameters,
            random_seed=random_seed
        )

        # 3. Evaluate model
        t_eval_start = time.perf_counter()
        metrics = self.evaluation.evaluate(
            model=model,
            X_val=X_val,
            y_val=y_val,
            training_duration_sec=train_duration
        )
        val_duration = time.perf_counter() - t_eval_start

        # 4. Save model artifact
        artifact_filename = f"{algorithm.lower()}_{model_version}.joblib"
        storage_path = self.persistence.save_model(model, artifact_filename)

        # 5. Register model
        registry_meta = self.registry.register_model(
            algorithm=algorithm,
            version=model_version,
            dataset_version=dataset_version,
            preprocessing_version=preprocessing_version,
            metrics=metrics,
            hyperparameters=hyperparameters,
            storage_path=storage_path,
            status="READY"
        )

        # 6. Log experiment run
        exp_meta_path = self.exp_logger.log_experiment(
            algorithm=algorithm,
            hyperparameters=hyperparameters,
            metrics=metrics,
            dataset_hash=dataset_hash,
            pipeline_version=preprocessing_version,
            model_version=model_version,
            training_duration_sec=train_duration,
            validation_duration_sec=val_duration
        )

        return {
            "status": "EXPERIMENT_SUCCESS",
            "model_id": registry_meta["model_id"],
            "model_version": model_version,
            "storage_path": storage_path,
            "metrics": metrics,
            "experiment_metadata_path": exp_meta_path
        }
