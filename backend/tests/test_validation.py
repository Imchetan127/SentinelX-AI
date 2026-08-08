import os
import json
import pytest
import numpy as np
import pandas as pd
from uuid import uuid4, UUID
from tempfile import TemporaryDirectory
from sqlalchemy.orm import Session
from sqlalchemy import select
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from app.database.session import SessionLocal, engine
from app.models import Base, Model, Dataset, AuditLog, ValidationResult
from app.models.enums import ModelStatus
from app.ml_engine.dataset_pipeline.pipeline import DatasetPipeline
from app.ml_engine.training.pipeline import TrainingService

from app.ml_engine.validation.loader import ModelLoader
from app.ml_engine.validation.metrics import MetricsAnalyzer
from app.ml_engine.validation.cross_validator import CrossValidator
from app.ml_engine.validation.threshold import ThresholdEvaluator, QualityGate
from app.ml_engine.validation.comparison import ComparisonEngine
from app.ml_engine.validation.reporter import ValidationReporter, REQUIRED_REPORT_FIELDS
from app.ml_engine.validation.benchmark import BenchmarkEngine
from app.ml_engine.validation.service import ValidationService


@pytest.fixture(scope="module")
def db() -> Session:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    ds = Dataset(name="cicids_test", version="v1.0")
    session.add(ds)
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def env_setup():
    with TemporaryDirectory() as tmp_dir:
        np.random.seed(42)
        n_samples = 200
        df = pd.DataFrame({
            "Flow Duration": np.random.randint(100, 100000, n_samples),
            "Total Fwd Packets": np.random.randint(1, 500, n_samples),
            "Fwd Packet Length Max": np.random.randint(10, 1500, n_samples),
            "Label": np.random.choice([0, 1], n_samples, p=[0.5, 0.5])
        })

        datasets_dir = os.path.join(tmp_dir, "datasets")
        raw_dir = os.path.join(datasets_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        df.to_csv(os.path.join(raw_dir, "cicids_test.csv"), index=False)

        dataset_pipe = DatasetPipeline(base_dir=datasets_dir, seed=42)
        dataset_pipe.run(
            raw_filename="cicids_test.csv",
            dataset_name="cicids_test",
            dataset_version="v1.0",
            preprocessing_version="p1.0",
            label_column="Label",
        )

        models_dir = os.path.join(tmp_dir, "models")
        trainer = TrainingService(base_dir=models_dir, datasets_dir=datasets_dir)

        # Train Model 1 (Random Forest)
        exp1 = trainer.run_training_experiment({
            "algorithm": "random_forest",
            "hyperparameters": {"n_estimators": 50, "random_state": 42},
            "dataset_name": "cicids_test",
            "dataset_version": "v1.0",
            "label_column": "Label",
        })

        # Train Model 2 (XGBoost)
        exp2 = trainer.run_training_experiment({
            "algorithm": "xgboost",
            "hyperparameters": {"n_estimators": 20, "max_depth": 3, "random_state": 42},
            "dataset_name": "cicids_test",
            "dataset_version": "v1.0",
            "label_column": "Label",
        })

        yield {
            "tmp_dir": tmp_dir,
            "models_dir": models_dir,
            "datasets_dir": datasets_dir,
            "exp1": exp1,
            "exp2": exp2,
        }


# ------------------------------------------------------------------
# Test Case 1: MetricsAnalyzer computes 18 metrics
# ------------------------------------------------------------------
def test_metrics_analyzer():
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(100, 4), columns=["f1", "f2", "f3", "f4"])
    y = pd.Series(np.random.choice([0, 1], 100))

    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)

    analyzer = MetricsAnalyzer()
    metrics = analyzer.compute(clf, X, y)

    # Verify key metrics exist and are correct type
    expected_keys = [
        "accuracy", "balanced_accuracy", "precision", "recall", "f1_score",
        "mcc", "roc_auc", "log_loss", "confusion_matrix", "false_positive_rate",
        "false_negative_rate", "specificity", "sensitivity", "support",
        "inference_latency_ms_per_sample", "prediction_throughput_per_sec",
        "class_report", "confidence_distribution"
    ]
    for key in expected_keys:
        assert key in metrics, f"Missing metric key: {key}"

    assert isinstance(metrics["accuracy"], float)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert isinstance(metrics["confusion_matrix"], list)
    assert len(metrics["confusion_matrix"]) == 2
    assert metrics["support"] == 100


# ------------------------------------------------------------------
# Test Case 2: CrossValidator produces mean, std, CI
# ------------------------------------------------------------------
def test_cross_validation():
    np.random.seed(42)
    X_train = pd.DataFrame(np.random.randn(80, 4))
    y_train = pd.Series(np.random.choice([0, 1], 80))
    X_val = pd.DataFrame(np.random.randn(20, 4))
    y_val = pd.Series(np.random.choice([0, 1], 20))

    clf = LogisticRegression(random_state=42)
    clf.fit(X_train, y_train)

    cv = CrossValidator(n_folds=5, random_state=42)
    cv_res = cv.run(clf, X_train, y_train, X_val, y_val)

    assert cv_res["n_folds"] == 5
    assert "accuracy" in cv_res["results"]
    acc_res = cv_res["results"]["accuracy"]

    assert "mean" in acc_res
    assert "std" in acc_res
    assert "ci_lower" in acc_res
    assert "ci_upper" in acc_res
    assert len(acc_res["fold_scores"]) == 5
    assert acc_res["ci_lower"] <= acc_res["mean"] <= acc_res["ci_upper"]


# ------------------------------------------------------------------
# Test Case 3: ThresholdEvaluator & QualityGate - PASS
# ------------------------------------------------------------------
def test_threshold_evaluator_pass():
    perfect_metrics = {
        "accuracy": 0.95,
        "precision": 0.93,
        "recall": 0.90,
        "f1_score": 0.91,
        "roc_auc": 0.96,
    }
    gate = QualityGate()
    verdict = gate.evaluate(perfect_metrics)

    assert verdict["result"] == QualityGate.RESULT_PASSED
    assert len(verdict["reasons"]) == 0
    assert len(verdict["threshold_results"]) == 5
    for tr in verdict["threshold_results"]:
        assert tr["passed"] is True


# ------------------------------------------------------------------
# Test Case 4: ThresholdEvaluator & QualityGate - FAIL
# ------------------------------------------------------------------
def test_threshold_evaluator_fail():
    failing_metrics = {
        "accuracy": 0.85,  # Below 0.90
        "precision": 0.92,
        "recall": 0.80,    # Below 0.85
        "f1_score": 0.85,  # Below 0.88
        "roc_auc": 0.95,
    }
    gate = QualityGate()
    verdict = gate.evaluate(failing_metrics)

    assert verdict["result"] == QualityGate.RESULT_FAILED
    assert len(verdict["reasons"]) == 3
    failed_metrics = [r["metric"] for r in verdict["threshold_results"] if not r["passed"]]
    assert "accuracy" in failed_metrics
    assert "recall" in failed_metrics
    assert "f1_score" in failed_metrics


# ------------------------------------------------------------------
# Test Case 5: Audit Events logged on validation
# ------------------------------------------------------------------
def test_quality_gate_audit_events(db: Session, env_setup):
    models_dir = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]
    exp1 = env_setup["exp1"]

    service = ValidationService(
        db,
        base_dir=models_dir,
        datasets_dir=datasets_dir,
        thresholds={"accuracy": 0.0, "f1_score": 0.0} # Ensure PASS regardless of synthetic model accuracy
    )

    res = service.validate_model(exp1["model_id"])
    assert res["quality_gate"]["result"] == "PASSED"

    # Query audit log entries for this action
    stmt = select(AuditLog).where(AuditLog.action.in_([
        "MODEL_VALIDATION_STARTED",
        "QUALITY_GATE_PASSED",
        "MODEL_VALIDATION_COMPLETED"
    ]))
    logs = db.scalars(stmt).all()
    actions = [log.action for log in logs]

    assert "MODEL_VALIDATION_STARTED" in actions
    assert "QUALITY_GATE_PASSED" in actions
    assert "MODEL_VALIDATION_COMPLETED" in actions


# ------------------------------------------------------------------
# Test Case 6: ComparisonEngine ranking and table generation
# ------------------------------------------------------------------
def test_comparison_engine():
    m1 = {
        "model_id": "m1",
        "algorithm": "random_forest",
        "version": "1.0",
        "metrics": {"accuracy": 0.95, "f1_score": 0.92, "roc_auc": 0.97, "inference_latency_ms_per_sample": 1.2},
        "quality_gate": {"result": "PASSED"}
    }
    m2 = {
        "model_id": "m2",
        "algorithm": "logistic_regression",
        "version": "1.0",
        "metrics": {"accuracy": 0.88, "f1_score": 0.84, "roc_auc": 0.90, "inference_latency_ms_per_sample": 0.2},
        "quality_gate": {"result": "FAILED"}
    }

    comp_engine = ComparisonEngine()
    comparison = comp_engine.compare([m1, m2])

    assert len(comparison["comparison_table"]) == 2
    assert comparison["summary"]["total_models"] == 2
    assert comparison["summary"]["passed"] == 1
    assert comparison["summary"]["failed"] == 1
    assert comparison["summary"]["best_f1_model"] == "m1"
    assert comparison["summary"]["fastest_model"] == "m2"

    # Check rankings for f1_score
    r1 = next(row for row in comparison["comparison_table"] if row["model_id"] == "m1")
    r2 = next(row for row in comparison["comparison_table"] if row["model_id"] == "m2")
    assert r1["ranks"]["f1_score"] == 1
    assert r2["ranks"]["f1_score"] == 2


# ------------------------------------------------------------------
# Test Case 7: ValidationService single model full pipeline
# ------------------------------------------------------------------
def test_validation_service_single_model(db: Session, env_setup):
    models_dir = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]
    exp1 = env_setup["exp1"]

    service = ValidationService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    res = service.validate_model(exp1["model_id"])

    assert res["model_id"] == exp1["model_id"]
    assert res["algorithm"] == "random_forest"
    assert res["metrics"] is not None
    assert res["cv_results"] is not None
    assert "validation_result_id" in res


# ------------------------------------------------------------------
# Test Case 8: Validation persistence in Database
# ------------------------------------------------------------------
def test_validation_persistence(db: Session, env_setup):
    models_dir = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]
    exp2 = env_setup["exp2"]

    service = ValidationService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    res = service.validate_model(exp2["model_id"])

    result_id = UUID(res["validation_result_id"])
    record = service.get_result_by_id(result_id)

    assert record is not None
    assert str(record.id) == str(result_id)
    assert record.validator_version == "1.0.0"
    assert record.quality_gate_result in ["PASSED", "FAILED"]
    assert record.report is not None


# ------------------------------------------------------------------
# Test Case 9: Report Generation completeness
# ------------------------------------------------------------------
def test_report_generation(env_setup):
    reporter = ValidationReporter()
    meta = {
        "model_id": "test-123",
        "algorithm": "xgboost",
        "version": "1.0.0",
        "dataset_version": "cicids_v1.0",
        "preprocessing_version": "p1.0",
    }
    metrics = {"accuracy": 0.92, "f1_score": 0.89}
    cv_results = {"n_folds": 5, "results": {}}
    gate = {"result": "PASSED", "reasons": [], "threshold_results": []}

    report = reporter.build_report(meta, metrics, cv_results, gate)

    # Check required fields
    for field_name in REQUIRED_REPORT_FIELDS:
        assert field_name in report, f"Missing report field: {field_name}"

    assert report["algorithm"] == "xgboost"
    assert report["quality_gate"]["result"] == "PASSED"


# ------------------------------------------------------------------
# Test Case 10: Model discovery skips ineligible (FAILED, ARCHIVED)
# ------------------------------------------------------------------
def test_model_discovery_skips_ineligible(env_setup):
    loader = ModelLoader(base_dir=env_setup["models_dir"])

    # Modify registry temporarily to include FAILED and ARCHIVED entries
    registry_path = os.path.join(env_setup["models_dir"], "registry", "registry.json")
    with open(registry_path, "r") as f:
        registry = json.load(f)

    # Add dummy entries
    failed_entry = dict(registry[0])
    failed_entry["model_id"] = str(uuid4())
    failed_entry["status"] = "FAILED"

    archived_entry = dict(registry[0])
    archived_entry["model_id"] = str(uuid4())
    archived_entry["status"] = "ARCHIVED"

    registry.extend([failed_entry, archived_entry])
    with open(registry_path, "w") as f:
        json.dump(registry, f)

    eligible = loader.get_eligible_models()
    eligible_ids = [m["model_id"] for m in eligible]

    assert failed_entry["model_id"] not in eligible_ids
    assert archived_entry["model_id"] not in eligible_ids
