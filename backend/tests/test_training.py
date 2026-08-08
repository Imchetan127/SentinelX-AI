import os
import json
import pytest
import numpy as np
import pandas as pd
from tempfile import TemporaryDirectory
from app.ml_engine.dataset_pipeline.pipeline import DatasetPipeline
from app.ml_engine.training.pipeline import TrainingService


@pytest.fixture(scope="module")
def prepared_dataset_dir():
    # Helper to generate test data splits using the pipeline
    with TemporaryDirectory() as tmp_dir:
        # Create raw test CSV
        np.random.seed(42)
        n_samples = 150
        df = pd.DataFrame({
            "Flow Duration": np.random.randint(100, 100000, n_samples),
            "Total Fwd Packets": np.random.randint(1, 500, n_samples),
            "Fwd Packet Length Max": np.random.randint(10, 1500, n_samples),
            "Label": np.random.choice(["BENIGN", "SQL Injection"], n_samples, p=[0.6, 0.4])
        })
        
        raw_dir = os.path.join(tmp_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        raw_path = os.path.join(raw_dir, "cicids_test.csv")
        df.to_csv(raw_path, index=False)

        # Run pipeline
        dataset_pipe = DatasetPipeline(base_dir=tmp_dir, seed=42)
        dataset_pipe.run(
            raw_filename="cicids_test.csv",
            dataset_name="cicids_test",
            dataset_version="v1.0",
            preprocessing_version="p1.0",
            label_column="Label"
        )
        
        # Return path so it persists during tests inside this directory
        yield tmp_dir


def test_training_pipeline_random_forest(prepared_dataset_dir):
    # Initialize training service pointing to mock datasets
    models_dir = os.path.join(prepared_dataset_dir, "models")
    training_service = TrainingService(base_dir=models_dir, datasets_dir=prepared_dataset_dir)

    config = {
        "algorithm": "random_forest",
        "random_seed": 42,
        "hyperparameters": {
            "n_estimators": 10,
            "max_depth": 5
        },
        "dataset_name": "cicids_test",
        "dataset_version": "v1.0",
        "preprocessing_version": "p1.0",
        "model_version": "1.0.0",
        "label_column": "Label"
    }

    res = training_service.run_training_experiment(config)
    assert res["status"] == "EXPERIMENT_SUCCESS"
    assert res["model_version"] == "1.0.0"
    
    # Check that model file is created
    assert os.path.exists(res["storage_path"])

    # Check metrics structure
    metrics = res["metrics"]
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "roc_auc" in metrics
    assert "confusion_matrix" in metrics
    assert "class_distribution" in metrics
    
    # Check registry was updated
    registry_list = training_service.registry.list_models()
    assert len(registry_list) == 1
    assert registry_list[0]["algorithm"] == "random_forest"
    assert registry_list[0]["version"] == "1.0.0"
    assert registry_list[0]["status"] == "READY"


def test_training_pipeline_xgboost(prepared_dataset_dir):
    models_dir = os.path.join(prepared_dataset_dir, "models")
    training_service = TrainingService(base_dir=models_dir, datasets_dir=prepared_dataset_dir)

    config = {
        "algorithm": "xgboost",
        "random_seed": 42,
        "hyperparameters": {
            "n_estimators": 10,
            "max_depth": 3
        },
        "dataset_name": "cicids_test",
        "dataset_version": "v1.0",
        "preprocessing_version": "p1.0",
        "model_version": "1.1.0",
        "label_column": "Label"
    }

    res = training_service.run_training_experiment(config)
    assert res["status"] == "EXPERIMENT_SUCCESS"
    assert res["model_version"] == "1.1.0"
    assert os.path.exists(res["storage_path"])
    
    # Check registry has both models now
    registry_list = training_service.registry.list_models()
    assert len(registry_list) == 2


def test_training_reproducibility(prepared_dataset_dir):
    models_dir = os.path.join(prepared_dataset_dir, "models")
    training_service1 = TrainingService(base_dir=models_dir, datasets_dir=prepared_dataset_dir)
    training_service2 = TrainingService(base_dir=models_dir, datasets_dir=prepared_dataset_dir)

    config1 = {
        "algorithm": "random_forest",
        "random_seed": 100,
        "hyperparameters": {"n_estimators": 5},
        "dataset_name": "cicids_test",
        "dataset_version": "v1.0",
        "preprocessing_version": "p1.0",
        "model_version": "rf_rep_1",
        "label_column": "Label"
    }

    config2 = {
        "algorithm": "random_forest",
        "random_seed": 100,
        "hyperparameters": {"n_estimators": 5},
        "dataset_name": "cicids_test",
        "dataset_version": "v1.0",
        "preprocessing_version": "p1.0",
        "model_version": "rf_rep_2",
        "label_column": "Label"
    }

    res1 = training_service1.run_training_experiment(config1)
    res2 = training_service2.run_training_experiment(config2)

    # Assert metrics are identical down to the decimals due to same seed
    assert res1["metrics"]["accuracy"] == res2["metrics"]["accuracy"]
    assert res1["metrics"]["f1_score"] == res2["metrics"]["f1_score"]
    assert res1["metrics"]["confusion_matrix"] == res2["metrics"]["confusion_matrix"]


def test_training_invalid_algorithm(prepared_dataset_dir):
    models_dir = os.path.join(prepared_dataset_dir, "models")
    training_service = TrainingService(base_dir=models_dir, datasets_dir=prepared_dataset_dir)

    config = {
        "algorithm": "invalid_alg",
        "dataset_name": "cicids_test",
        "dataset_version": "v1.0",
        "label_column": "Label"
    }

    with pytest.raises(ValueError, match="Unsupported algorithm"):
        training_service.run_training_experiment(config)


def test_training_missing_dataset_fails(prepared_dataset_dir):
    models_dir = os.path.join(prepared_dataset_dir, "models")
    training_service = TrainingService(base_dir=models_dir, datasets_dir=prepared_dataset_dir)

    config = {
        "algorithm": "random_forest",
        "dataset_name": "non_existent_dataset",
        "dataset_version": "v9.9",
        "label_column": "Label"
    }

    with pytest.raises(FileNotFoundError):
        training_service.run_training_experiment(config)


def test_persistence_prevents_overwrite(prepared_dataset_dir):
    models_dir = os.path.join(prepared_dataset_dir, "models")
    training_service = TrainingService(base_dir=models_dir, datasets_dir=prepared_dataset_dir)

    config = {
        "algorithm": "random_forest",
        "random_seed": 42,
        "hyperparameters": {"n_estimators": 5},
        "dataset_name": "cicids_test",
        "dataset_version": "v1.0",
        "preprocessing_version": "p1.0",
        "model_version": "rf_overwrite_test",
        "label_column": "Label"
    }

    # Run once
    training_service.run_training_experiment(config)
    
    # Run again with same version (should fail on saving)
    with pytest.raises(ValueError, match="version conflict"):
        training_service.run_training_experiment(config)
