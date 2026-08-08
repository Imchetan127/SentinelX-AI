import os
import json
import pytest
import numpy as np
import pandas as pd
from uuid import uuid4
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import SessionLocal, engine
from app.models import Base, Detection, Prediction, AuditLog, Model, Dataset, Attack
from app.models.enums import Severity, AttackStatus
from app.ml_engine.dataset_pipeline.pipeline import DatasetPipeline
from app.ml_engine.training.pipeline import TrainingService
from app.ml_engine.inference.engine import InferenceService


@pytest.fixture(scope="module")
def db() -> Session:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    # Ensure there is a default dataset row for Model foreign key constraints
    ds = Dataset(name="cicids_test", version="v1.0")
    session.add(ds)
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def ml_environment():
    # Setup test dataset and train models
    with TemporaryDirectory() as tmp_dir:
        # Create raw test CSV
        np.random.seed(42)
        n_samples = 100
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
        
        # Train and register Model 1: Random Forest
        models_dir = os.path.join(tmp_dir, "models")
        training_service = TrainingService(base_dir=models_dir, datasets_dir=tmp_dir)

        config1 = {
            "algorithm": "random_forest",
            "random_seed": 42,
            "hyperparameters": {"n_estimators": 5},
            "dataset_name": "cicids_test",
            "dataset_version": "v1.0",
            "preprocessing_version": "p1.0",
            "model_version": "1.0.0",
            "label_column": "Label"
        }
        training_service.run_training_experiment(config1)

        # Train and register Model 2: XGBoost
        config2 = {
            "algorithm": "xgboost",
            "random_seed": 42,
            "hyperparameters": {"n_estimators": 5},
            "dataset_name": "cicids_test",
            "dataset_version": "v1.0",
            "preprocessing_version": "p1.0",
            "model_version": "2.0.0",
            "label_column": "Label"
        }
        training_service.run_training_experiment(config2)

        yield tmp_dir


def test_inference_valid(db: Session, ml_environment):
    models_dir = os.path.join(ml_environment, "models")
    inference_service = InferenceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    # Clear prior cache
    InferenceService._cached_model_id = None
    InferenceService._cached_model = None

    # Create Attack and Detection record
    attack = Attack(
        type="SQL Injection",
        payload="SELECT 1",
        target="system",
        severity=Severity.HIGH,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(attack)
    db.flush()

    detection = Detection(
        attack_id=attack.id,
        severity=Severity.HIGH,
        attack_type="SQL Injection",
        recommendation="Validate parameter types",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(detection)
    db.commit()

    features = {
        "Flow Duration": 12000,
        "Total Fwd Packets": 45,
        "Fwd Packet Length Max": 1100
    }

    # Run inference
    res = inference_service.predict_raw(
        features_dict=features,
        detection_id=detection.id
    )

    assert "prediction" in res
    assert res["prediction"] in ["clean", "malicious"]
    assert "confidence" in res
    assert res["model_version"] == "2.0.0"  # XGBoost was trained last, so it is the active fallback model
    
    # Check that Prediction is persisted in DB
    db_pred = db.scalars(select(Prediction).where(Prediction.detection_id == detection.id)).first()
    assert db_pred is not None
    assert db_pred.prediction == res["prediction"]

    # Verify audit logs generated
    audit_logs = db.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5)).all()
    actions = [log.action for log in audit_logs]
    assert "MODEL_LOADED" in actions
    assert "PREDICTION_EXECUTED" in actions


def test_inference_invalid_feature_count(db: Session, ml_environment):
    # Call rollback to clear any potential previous pending transaction states
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    inference_service = InferenceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    attack = Attack(
        type="DDoS",
        payload="1000 requests/s",
        target="system",
        severity=Severity.MEDIUM,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(attack)
    db.flush()

    detection = Detection(
        attack_id=attack.id,
        severity=Severity.MEDIUM,
        attack_type="DDoS",
        recommendation="Rate limit incoming requests",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(detection)
    db.commit()

    # Pass 2 features instead of 3 expected features
    features = {
        "Flow Duration": 12000,
        "Total Fwd Packets": 45
    }

    with pytest.raises(ValueError, match="Feature validation failed"):
        inference_service.predict_raw(features, detection.id)

    # Check validation failed audit log is written
    audit = db.scalars(select(AuditLog).where(AuditLog.action == "VALIDATION_FAILED").order_by(AuditLog.timestamp.desc())).first()
    assert audit is not None
    assert "Missing feature" in audit.details


def test_inference_nan_value(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    inference_service = InferenceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    attack = Attack(
        type="Spam",
        payload="Subject: Click here",
        target="system",
        severity=Severity.LOW,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(attack)
    db.flush()

    detection = Detection(
        attack_id=attack.id,
        severity=Severity.LOW,
        attack_type="Spam",
        recommendation="Filter spam email",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(detection)
    db.commit()

    # Pass NaN values in features
    features = {
        "Flow Duration": 12000,
        "Total Fwd Packets": np.nan,
        "Fwd Packet Length Max": 800
    }

    with pytest.raises(ValueError, match="NaN / missing value"):
        inference_service.predict_raw(features, detection.id)


def test_inference_caching_and_repeated_inference(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    inference_service = InferenceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    attack = Attack(
        type="SQL Injection",
        payload="UNION SELECT",
        target="system",
        severity=Severity.HIGH,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(attack)
    db.flush()

    detection = Detection(
        attack_id=attack.id,
        severity=Severity.HIGH,
        attack_type="SQL Injection",
        recommendation="Use prepared statements",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(detection)
    db.commit()

    features = {
        "Flow Duration": 20000,
        "Total Fwd Packets": 200,
        "Fwd Packet Length Max": 1200
    }

    # First call will load model from disk (cache miss)
    InferenceService._cached_model_id = None
    res1 = inference_service.predict_raw(features, detection.id)
    cached_id = InferenceService._cached_model_id
    assert cached_id is not None

    # Audit log counts before second call
    loaded_audits_before = len(db.scalars(select(AuditLog).where(AuditLog.action == "MODEL_LOADED")).all())

    # Second call should use cache (no new MODEL_LOADED logs)
    res2 = inference_service.predict_raw(features, detection.id)
    assert res2["prediction"] == res1["prediction"]
    
    loaded_audits_after = len(db.scalars(select(AuditLog).where(AuditLog.action == "MODEL_LOADED")).all())
    assert loaded_audits_before == loaded_audits_after


def test_inference_model_switching(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    inference_service = InferenceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    attack = Attack(
        type="SQL Injection",
        payload="UNION SELECT",
        target="system",
        severity=Severity.HIGH,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(attack)
    db.flush()

    detection = Detection(
        attack_id=attack.id,
        severity=Severity.HIGH,
        attack_type="SQL Injection",
        recommendation="Prepared statements",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(detection)
    db.commit()

    features = {
        "Flow Duration": 20000,
        "Total Fwd Packets": 200,
        "Fwd Packet Length Max": 1200
    }

    # Resolve models registry file path
    reg_path = os.path.join(models_dir, "registry", "registry.json")
    with open(reg_path, "r") as f:
        registry = json.load(f)

    # Currently active fallback is version 2.0.0. Let's explicitly set status of version 1.0.0 to "ACTIVE"
    for item in registry:
        if item["version"] == "1.0.0":
            item["status"] = "ACTIVE"
        else:
            item["status"] = "VALIDATED"

    with open(reg_path, "w") as f:
        json.dump(registry, f, indent=4)

    # Invalidate cached variables to ensure cache invalidation happens dynamically
    res = inference_service.predict_raw(features, detection.id)
    assert res["model_version"] == "1.0.0"  # Model switching was successfully caught!

    # Verify that a MODEL_LOADED audit log is emitted for switching versions
    audit = db.scalars(select(AuditLog).where(
        AuditLog.action == "MODEL_LOADED", 
        AuditLog.details.like("%v1.0.0%")
    ).order_by(AuditLog.timestamp.desc())).first()
    assert audit is not None


def test_inference_missing_model_registry(db: Session):
    db.rollback()
    # Pass a non-existent base directory
    inference_service = InferenceService(db, base_dir="/non_existent_path")

    attack = Attack(
        type="DDoS",
        payload="1000 requests/s",
        target="system",
        severity=Severity.MEDIUM,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(attack)
    db.flush()
    
    detection = Detection(
        attack_id=attack.id,
        severity=Severity.MEDIUM,
        attack_type="DDoS",
        recommendation="Limit",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(detection)
    db.commit()

    with pytest.raises(RuntimeError, match="No model registry database exists"):
        inference_service.predict_raw({"col": 1}, detection.id)
