"""ModelLoader — loads a trained model artifact and its dataset splits.

Responsibilities
----------------
- Locate the model binary via the registry `storage_path`.
- Load the fitted preprocessing scaler for the associated dataset version.
- Load the processed train, val, and test CSV splits.
- Return a structured payload consumed by BenchmarkEngine.

Does NOT modify inference logic, retrain models, or write to the registry.
"""
import os
import json
import logging
import joblib
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("Validation.ModelLoader")

# File-name convention shared with DatasetPipeline and TrainingService
_SPLIT_SUFFIXES = {"train": "_train.csv", "val": "_val.csv", "test": "_test.csv"}


class ModelLoader:
    """Loads a model artifact and its associated dataset splits."""

    def __init__(self, base_dir: str = "../models", datasets_dir: str = "../datasets"):
        self.base_dir = base_dir
        self.datasets_dir = datasets_dir
        self.registry_filepath = os.path.join(base_dir, "registry", "registry.json")

    # ------------------------------------------------------------------
    # Registry helpers
    # ------------------------------------------------------------------

    def load_registry(self) -> List[Dict[str, Any]]:
        """Return the full registry list or raise RuntimeError on corruption."""
        if not os.path.exists(self.registry_filepath):
            raise RuntimeError(
                f"Model registry not found at: {self.registry_filepath}"
            )
        try:
            with open(self.registry_filepath, "r") as f:
                return json.load(f)
        except Exception as exc:
            raise RuntimeError(f"Corrupt model registry: {exc}") from exc

    def get_eligible_models(self) -> List[Dict[str, Any]]:
        """Return registry entries whose status is VALIDATED, STAGING, or PRODUCTION.

        FAILED and ARCHIVED models are excluded.
        """
        registry = self.load_registry()
        eligible_statuses = {"VALIDATED", "STAGING", "PRODUCTION"}
        eligible = []
        for entry in registry:
            status = (entry.get("status") or "").upper()
            if status in eligible_statuses:
                eligible.append(entry)
            else:
                logger.info(
                    "Skipping model '%s' (status=%s) — not eligible for validation.",
                    entry.get("model_id", "?"), status
                )
        return eligible

    def get_model_meta(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Return the registry entry for *model_id*, or None if absent."""
        registry = self.load_registry()
        return next((m for m in registry if m.get("model_id") == model_id), None)

    # ------------------------------------------------------------------
    # Artifact loading
    # ------------------------------------------------------------------

    def load_model_artifact(self, storage_path: str) -> Any:
        """Load and return the joblib model object from *storage_path*."""
        if not storage_path or not os.path.exists(storage_path):
            raise FileNotFoundError(
                f"Model artifact not found at: {storage_path!r}"
            )
        try:
            model = joblib.load(storage_path)
            logger.info("Loaded model artifact from: %s", storage_path)
            return model
        except Exception as exc:
            raise RuntimeError(f"Failed to deserialise model artifact: {exc}") from exc

    def load_scaler(self, dataset_name: str, dataset_version: str) -> Any:
        """Load the fitted preprocessing scaler for the given dataset version."""
        scaler_filename = f"{dataset_name}_{dataset_version}_scaler.joblib"
        scaler_path = os.path.join(self.datasets_dir, "processed", scaler_filename)
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(
                f"Preprocessing scaler not found at: {scaler_path!r}"
            )
        try:
            scaler = joblib.load(scaler_path)
            logger.info("Loaded scaler from: %s", scaler_path)
            return scaler
        except Exception as exc:
            raise RuntimeError(f"Failed to load scaler: {exc}") from exc

    # ------------------------------------------------------------------
    # Dataset split loading
    # ------------------------------------------------------------------

    def load_splits(
        self,
        dataset_name: str,
        dataset_version: str,
        label_column: str = "Label",
    ) -> Dict[str, Tuple[pd.DataFrame, pd.Series]]:
        """Return {split_name: (X, y)} for train, val, and test."""
        processed_dir = os.path.join(self.datasets_dir, "processed")
        splits: Dict[str, Tuple[pd.DataFrame, pd.Series]] = {}

        for split_name, suffix in _SPLIT_SUFFIXES.items():
            path = os.path.join(
                processed_dir, f"{dataset_name}_{dataset_version}{suffix}"
            )
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Processed split '{split_name}' not found at: {path!r}"
                )
            try:
                df = pd.read_csv(path)
            except Exception as exc:
                raise ValueError(
                    f"Failed to parse split '{split_name}' at {path!r}: {exc}"
                ) from exc

            if label_column not in df.columns:
                raise ValueError(
                    f"Label column '{label_column}' missing from split '{split_name}'. "
                    f"Available columns: {list(df.columns)}"
                )
            X = df.drop(columns=[label_column])
            y = df[label_column]
            splits[split_name] = (X, y)

        logger.info(
            "Loaded splits for %s_%s: train=%d, val=%d, test=%d rows.",
            dataset_name, dataset_version,
            len(splits["train"][0]),
            len(splits["val"][0]),
            len(splits["test"][0]),
        )
        return splits

    # ------------------------------------------------------------------
    # Convenience: full payload
    # ------------------------------------------------------------------

    def load_for_validation(
        self,
        model_meta: Dict[str, Any],
        label_column: str = "Label",
    ) -> Dict[str, Any]:
        """Return a complete validation payload dict for *model_meta*.

        Keys returned
        -------------
        model        : the loaded sklearn / XGBoost estimator
        splits       : {split_name: (X, y)}
        scaler       : the fitted preprocessing scaler
        dataset_name : str
        dataset_version : str
        preprocessing_version : str
        """
        dataset_ver = model_meta.get("dataset_version") or "cicids_test_v1.0"
        if "_" in dataset_ver:
            dataset_name, dataset_version = dataset_ver.split("_", 1)
        else:
            dataset_name, dataset_version = "cicids_test", dataset_ver

        model = self.load_model_artifact(model_meta["storage_path"])
        scaler = self.load_scaler(dataset_name, dataset_version)
        splits = self.load_splits(dataset_name, dataset_version, label_column)

        return {
            "model":                model,
            "splits":               splits,
            "scaler":               scaler,
            "dataset_name":         dataset_name,
            "dataset_version":      dataset_version,
            "preprocessing_version": model_meta.get("preprocessing_version", "unknown"),
        }
