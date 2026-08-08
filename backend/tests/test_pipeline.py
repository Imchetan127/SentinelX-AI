import os
import json
import pytest
import numpy as np
import pandas as pd
from tempfile import TemporaryDirectory
from app.ml_engine.dataset_pipeline.loader import DatasetLoader
from app.ml_engine.dataset_pipeline.validator import DatasetValidator
from app.ml_engine.dataset_pipeline.cleaner import DatasetCleaner
from app.ml_engine.dataset_pipeline.transformer import FeatureTransformer
from app.ml_engine.dataset_pipeline.splitter import DatasetSplitter
from app.ml_engine.dataset_pipeline.metadata import MetadataManager
from app.ml_engine.dataset_pipeline.pipeline import DatasetPipeline


def test_loader_missing_file_fails_loudly():
    loader = DatasetLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("non_existent_file.csv")


def test_loader_empty_file_fails_loudly(tmp_path):
    loader = DatasetLoader()
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    with pytest.raises(ValueError, match="empty"):
        loader.load(str(empty_file))


def test_loader_corrupted_csv_fails_loudly(tmp_path):
    loader = DatasetLoader()
    corrupt_file = tmp_path / "corrupt.csv"
    corrupt_file.write_bytes(b"\x00\xff\x00\xff\ncorruptedbinarydata")

    with pytest.raises(ValueError):
        loader.load(str(corrupt_file))


def test_loader_missing_required_columns(tmp_path):
    loader = DatasetLoader()
    test_file = tmp_path / "test.csv"
    pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}).to_csv(test_file, index=False)

    with pytest.raises(ValueError, match="columns missing"):
        loader.load(str(test_file), required_columns=["col1", "col_missing"])


def test_validator_empty_dataframe():
    validator = DatasetValidator()
    with pytest.raises(ValueError, match="empty"):
        validator.validate(pd.DataFrame())


def test_cleaner_and_transformer_operations():
    # Setup test dataframe containing duplicates, NaN, Inf, and diverse labels
    df = pd.DataFrame({
        "Flow Duration": [100, 100, 200, 300, np.nan, 400],
        "Fwd Packets": [10, 10, 20, np.inf, 30, -np.inf],
        "Label": ["BENIGN", "BENIGN", "SQL Injection", "benign", "Normal", "DDoS"]
    })

    # Validate stats first
    validator = DatasetValidator()
    stats = validator.validate(df, label_column="Label")
    assert stats["row_count"] == 6
    assert stats["duplicate_rows"] == 1  # Row index 1 is duplicate of index 0
    assert stats["total_missing_values"] == 1  # 1 NaN in Flow Duration

    # Clean data
    cleaner = DatasetCleaner()
    cleaned_df = cleaner.clean(df, label_column="Label")
    assert len(cleaned_df) == 5  # Duplicate removed
    
    # Check that inf and NaN are filled with column medians
    assert cleaned_df["Flow Duration"].isnull().sum() == 0
    assert cleaned_df["Fwd Packets"].isnull().sum() == 0
    assert np.isinf(cleaned_df["Fwd Packets"]).sum() == 0

    # Transform targets
    transformer = FeatureTransformer()
    X, y = transformer.split_features_target(cleaned_df, label_column="Label")
    y_norm = transformer.normalize_target(y)
    
    # Assert benign/normal are mapped to 0, attacks to 1
    # Cleaned rows:
    # 0: [100, 10, BENIGN] -> [100, 10, 0]
    # 2: [200, 20, SQL Injection] -> [200, 20, 1]
    # 3: [300, median, benign] -> [300, median, 0]
    # 4: [median, 30, Normal] -> [median, 30, 0]
    # 5: [400, median, DDoS] -> [400, median, 1]
    expected_normalized = [0, 1, 0, 0, 1]
    assert list(y_norm) == expected_normalized


def test_pipeline_reproducibility():
    # Write a test CSV with multiple rows
    np.random.seed(42)
    n_samples = 100
    df = pd.DataFrame({
        "Flow Duration": np.random.randint(100, 100000, n_samples),
        "Total Fwd Packets": np.random.randint(1, 500, n_samples),
        "Fwd Packet Length Max": np.random.randint(10, 1500, n_samples),
        "Label": np.random.choice(["BENIGN", "SQL Injection"], n_samples, p=[0.7, 0.3])
    })

    with TemporaryDirectory() as tmp_dir:
        raw_dir = os.path.join(tmp_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        raw_path = os.path.join(raw_dir, "cicids2017_test.csv")
        df.to_csv(raw_path, index=False)

        # Setup and run pipeline runs
        pipeline1 = DatasetPipeline(scaling_strategy="standard", base_dir=tmp_dir, seed=123)
        res1 = pipeline1.run(
            raw_filename="cicids2017_test.csv",
            dataset_name="cicids_test",
            dataset_version="v1",
            preprocessing_version="p1",
            label_column="Label"
        )

        pipeline2 = DatasetPipeline(scaling_strategy="standard", base_dir=tmp_dir, seed=123)
        res2 = pipeline2.run(
            raw_filename="cicids2017_test.csv",
            dataset_name="cicids_test",
            dataset_version="v1",
            preprocessing_version="p1",
            label_column="Label"
        )

        # Assert identical durations are deterministic or matching metadata hashes
        meta1 = res1["metadata"]
        meta2 = res2["metadata"]

        assert meta1["row_count"] == meta2["row_count"]
        assert meta1["feature_count"] == meta2["feature_count"]
        assert meta1["label_distribution"] == meta2["label_distribution"]
        
        # Check files match byte-for-byte using checksum hashes
        assert meta1["file_hashes"] == meta2["file_hashes"]
        assert meta1["file_hashes"]["train"] != ""
        assert meta1["file_hashes"]["val"] != ""
        assert meta1["file_hashes"]["test"] != ""

        # Verify splits can be read and scaling is correct
        df_train = pd.read_csv(res1["filepaths"]["train"])
        expected_size = res1["metadata"]["row_count"] * 0.7
        assert abs(len(df_train) - expected_size) <= 2
        assert "Label" in df_train.columns
