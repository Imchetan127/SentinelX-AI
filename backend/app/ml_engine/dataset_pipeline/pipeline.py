import os
import time
import logging
import pandas as pd
from typing import Dict, Any, List, Optional

from app.ml_engine.dataset_pipeline.loader import DatasetLoader
from app.ml_engine.dataset_pipeline.validator import DatasetValidator
from app.ml_engine.dataset_pipeline.cleaner import DatasetCleaner
from app.ml_engine.dataset_pipeline.transformer import FeatureTransformer
from app.ml_engine.dataset_pipeline.splitter import DatasetSplitter
from app.ml_engine.dataset_pipeline.metadata import MetadataManager

logger = logging.getLogger("DatasetPipeline.Coordinator")


class DatasetPipeline:
    def __init__(
        self,
        scaling_strategy: str = "standard",
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42,
        base_dir: str = "../datasets"
    ):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, "raw")
        self.processed_dir = os.path.join(base_dir, "processed")
        self.metadata_dir = os.path.join(base_dir, "metadata")

        # Initialize subcomponents
        self.loader = DatasetLoader()
        self.validator = DatasetValidator()
        self.cleaner = DatasetCleaner()
        self.transformer = FeatureTransformer(scaling_strategy=scaling_strategy)
        self.splitter = DatasetSplitter(
            train_ratio=train_ratio,
            val_ratio=val_ratio,
            test_ratio=test_ratio,
            seed=seed
        )
        self.metadata_mgr = MetadataManager(metadata_dir=self.metadata_dir)

    def run(
        self,
        raw_filename: str,
        dataset_name: str,
        dataset_version: str,
        preprocessing_version: str,
        label_column: str = "Label",
        required_columns: Optional[List[str]] = None,
        expected_labels: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        t_start = time.time()
        logger.info(f"Launching dataset pipeline execution for scenario: {dataset_name} v{dataset_version}")

        # Ensure directory structures are populated
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)

        raw_filepath = os.path.join(self.raw_dir, raw_filename)

        # 1. Loading Phase
        df_raw = self.loader.load(raw_filepath, required_columns=required_columns)

        # 2. Validation Phase (Statistics of Raw dataset)
        raw_stats = self.validator.validate(df_raw, label_column=label_column, expected_labels=expected_labels)

        # 3. Cleaning Phase
        df_cleaned = self.cleaner.clean(df_raw, label_column=label_column)
        rows_removed = len(df_raw) - len(df_cleaned)

        # 4. Feature Extraction & Separation
        X, y = self.transformer.split_features_target(df_cleaned, label_column=label_column)
        
        # Target Normalization
        y_normalized = self.transformer.normalize_target(y)

        # 5. Reproducible Data Splitting
        splits = self.splitter.split(X, y_normalized)
        X_train, y_train = splits["train"]
        X_val, y_val = splits["val"]
        X_test, y_test = splits["test"]

        # 6. Feature Scaling (fit on Train, transform all)
        self.transformer.fit_scaler(X_train)
        X_train_scaled = self.transformer.transform_features(X_train)
        X_val_scaled = self.transformer.transform_features(X_val)
        X_test_scaled = self.transformer.transform_features(X_test)

        # Save fitted scaler object for inference serving
        import joblib
        scaler_filename = f"{dataset_name}_{dataset_version}_scaler.joblib"
        scaler_filepath = os.path.join(self.processed_dir, scaler_filename)
        joblib.dump(self.transformer.scaler, scaler_filepath)
        logger.info(f"Saved fitted scaler object to: {scaler_filepath}")

        # 7. Merge features and targets back for output storage
        train_out = X_train_scaled.copy()
        train_out[label_column] = y_train

        val_out = X_val_scaled.copy()
        val_out[label_column] = y_val

        test_out = X_test_scaled.copy()
        test_out[label_column] = y_test

        # Save processed CSV files
        filepaths = {
            "train": os.path.join(self.processed_dir, f"{dataset_name}_{dataset_version}_train.csv"),
            "val": os.path.join(self.processed_dir, f"{dataset_name}_{dataset_version}_val.csv"),
            "test": os.path.join(self.processed_dir, f"{dataset_name}_{dataset_version}_test.csv"),
        }

        train_out.to_csv(filepaths["train"], index=False)
        val_out.to_csv(filepaths["val"], index=False)
        test_out.to_csv(filepaths["test"], index=False)

        # 8. Metadata Generation and Exporting
        counts = y_normalized.value_counts(dropna=False)
        normalized_label_dist = {str(k): int(v) for k, v in counts.items()}

        duration = round(time.time() - t_start, 3)
        logger.info(f"Dataset pipeline completed successfully in {duration} seconds.")

        meta_report = self.metadata_mgr.generate_and_save(
            filepaths=filepaths,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            preprocessing_version=preprocessing_version,
            row_count=len(df_cleaned),
            feature_count=len(X.columns),
            label_distribution=normalized_label_dist,
            validation_stats=raw_stats
        )

        return {
            "status": "PIPELINE_SUCCESS",
            "duration_sec": duration,
            "rows_processed": len(df_raw),
            "rows_removed": rows_removed,
            "filepaths": filepaths,
            "metadata": meta_report,
        }
