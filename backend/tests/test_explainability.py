"""tests/test_explainability.py — Sprint 4.1 XAI test suite.

8 test cases:
  1. Random Forest SHAP explanations
  2. XGBoost SHAP explanations
  3. Unsupported model type rejection
  4. Prediction linkage validation
  5. Explanation persistence in DB
  6. ExplanationValidator catches feature mismatch
  7. Audit events logged correctly
  8. Deterministic repeated explanations
"""
import os
import json
import pytest
import numpy as np
import pandas as pd
from uuid import uuid4, UUID
from datetime import datetime, timezone
from tempfile import TemporaryDirectory

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import SessionLocal, engine
from app.models import Base, Model, Dataset, AuditLog, Explanation
from app.models.attack import Attack
from app.models.detection import Detection
from app.models.prediction import Prediction
from app.models.enums import Severity, AttackStatus

from app.ml_engine.dataset_pipeline.pipeline import DatasetPipeline
from app.ml_engine.training.pipeline import TrainingService
from app.ml_engine.inference.engine import InferenceService
from app.ml_engine.explainability.service import ExplainabilityService
from app.ml_engine.explainability.shap_engine import SHAPEngine, UnsupportedModelError
from app.ml_engine.explainability.validator import ExplanationValidator, ExplanationValidationError
from app.ml_engine.explainability.audit import (
    EVENT_GENERATED, EVENT_FAILED, EVENT_VALIDATED
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

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
    """Train one Random Forest and one XGBoost model; yield the tmp dir."""
    with TemporaryDirectory() as tmp_dir:
        np.random.seed(42)
        n_samples = 120

        df = pd.DataFrame({
            "Flow Duration":        np.random.randint(100, 100_000, n_samples),
            "Total Fwd Packets":    np.random.randint(1, 500, n_samples),
            "Fwd Packet Length Max": np.random.randint(10, 1_500, n_samples),
            "Label":                np.random.choice(["BENIGN", "Attack"], n_samples),
        })

        datasets_dir = os.path.join(tmp_dir, "datasets")
        raw_dir      = os.path.join(datasets_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        df.to_csv(os.path.join(raw_dir, "cicids_test.csv"), index=False)

        pipe = DatasetPipeline(base_dir=datasets_dir, seed=42)
        pipe.run(
            raw_filename="cicids_test.csv",
            dataset_name="cicids_test",
            dataset_version="v1.0",
            preprocessing_version="p1.0",
            label_column="Label",
        )

        models_dir = os.path.join(tmp_dir, "models")
        trainer    = TrainingService(base_dir=models_dir, datasets_dir=datasets_dir)

        trainer.run_training_experiment({
            "algorithm": "random_forest",
            "hyperparameters": {"n_estimators": 10, "random_state": 42},
            "dataset_name": "cicids_test",
            "dataset_version": "v1.0",
            "preprocessing_version": "p1.0",
            "model_version": "1.0.0",
            "label_column": "Label",
        })
        trainer.run_training_experiment({
            "algorithm": "xgboost",
            "hyperparameters": {"n_estimators": 10, "random_state": 42},
            "dataset_name": "cicids_test",
            "dataset_version": "v1.0",
            "preprocessing_version": "p1.0",
            "model_version": "2.0.0",
            "label_column": "Label",
        })

        yield {
            "tmp_dir":      tmp_dir,
            "models_dir":   models_dir,
            "datasets_dir": datasets_dir,
        }


def _make_detection(db):
    """Helper: create a minimal Attack + Detection row and return detection.id."""
    attack = Attack(
        type="SQL Injection", payload="UNION SELECT",
        target="system", severity=Severity.HIGH,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(attack)
    db.flush()
    detection = Detection(
        attack_id=attack.id, severity=Severity.HIGH,
        attack_type="SQL Injection",
        recommendation="Use prepared statements",
        detected_at=datetime.now(timezone.utc)
    )
    db.add(detection)
    db.commit()
    return detection.id


FEATURES = {
    "Flow Duration":        12_000,
    "Total Fwd Packets":    45,
    "Fwd Packet Length Max": 1_100,
}


# ---------------------------------------------------------------------------
# Test 1: Random Forest SHAP explanations
# ---------------------------------------------------------------------------
def test_shap_random_forest(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    # Force RF (v1.0.0) to be ACTIVE in registry
    reg_path = os.path.join(models_dir, "registry", "registry.json")
    with open(reg_path) as f:
        registry = json.load(f)
    for m in registry:
        m["status"] = "ACTIVE" if m["version"] == "1.0.0" else "VALIDATED"
    with open(reg_path, "w") as f:
        json.dump(registry, f)

    InferenceService._cached_model_id = None   # invalidate cache

    detection_id = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result  = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    result = svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)

    assert result["algorithm"] == "random_forest"
    assert len(result["shap_values"]) == 3   # 3 features
    assert len(result["feature_names"]) == 3
    assert result["base_value"] is not None
    assert "feature_importance" in result
    assert len(result["feature_importance"]) == 3


# ---------------------------------------------------------------------------
# Test 2: XGBoost SHAP explanations
# ---------------------------------------------------------------------------
def test_shap_xgboost(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    # Force XGBoost (v2.0.0) to be ACTIVE
    reg_path = os.path.join(models_dir, "registry", "registry.json")
    with open(reg_path) as f:
        registry = json.load(f)
    for m in registry:
        m["status"] = "ACTIVE" if m["version"] == "2.0.0" else "VALIDATED"
    with open(reg_path, "w") as f:
        json.dump(registry, f)

    InferenceService._cached_model_id = None

    detection_id  = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result   = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    result = svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)

    assert result["algorithm"] == "xgboost"
    assert len(result["shap_values"]) == 3
    assert isinstance(result["base_value"], float)
    assert any(c["feature"] in FEATURES for c in result["feature_importance"])


# ---------------------------------------------------------------------------
# Test 3: Unsupported model type raises UnsupportedModelError
# ---------------------------------------------------------------------------
def test_unsupported_model_rejection():
    """UnsupportedModelError must be raised before any SHAP call is attempted."""
    # The algorithm-name check fires immediately; no real model is needed.
    class _DummyModel:
        pass

    X = pd.DataFrame({"a": [0.1], "b": [0.2]})
    engine = SHAPEngine()

    with pytest.raises(UnsupportedModelError) as exc_info:
        engine.explain(
            model=_DummyModel(),
            algorithm="logistic_regression",
            X_scaled=X,
            feature_names=["a", "b"],
        )
    assert "logistic_regression" in str(exc_info.value)
    assert "random_forest" in str(exc_info.value) or "xgboost" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Test 4: Prediction linkage — explanation is linked to the correct prediction
# ---------------------------------------------------------------------------
def test_prediction_linkage(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    InferenceService._cached_model_id = None

    detection_id  = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result   = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    result = svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)

    assert result["prediction_id"] == str(prediction_id)
    assert result["prediction"] in ("malicious", "clean")


# ---------------------------------------------------------------------------
# Test 5: Explanation is persisted and retrievable from DB
# ---------------------------------------------------------------------------
def test_explanation_persistence(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    InferenceService._cached_model_id = None

    detection_id  = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result   = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    result = svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)

    db_expl = svc.get_latest_for_prediction(prediction_id)
    assert db_expl is not None
    assert str(db_expl.prediction_id) == str(prediction_id)
    assert db_expl.base_value is not None
    assert isinstance(db_expl.shap_values, list)
    assert len(db_expl.shap_values) == 3


# ---------------------------------------------------------------------------
# Test 6: Validation — mismatched SHAP dimensions raise ExplanationValidationError
# ---------------------------------------------------------------------------
def test_validation_rules(db: Session):
    db.rollback()
    validator = ExplanationValidator(db)

    # Use a random prediction_id that doesn't exist in DB → fails Rule 1
    fake_id = uuid4()
    shap_output = {
        "base_value":   0.3,
        "shap_values":  [0.1, 0.2],        # 2 values
        "feature_names": ["f1", "f2", "f3"], # but 3 names → mismatch (Rule 3)
    }

    with pytest.raises(ExplanationValidationError) as exc_info:
        validator.validate(
            prediction_id=fake_id,
            model_id=uuid4(),
            shap_output=shap_output,
        )
    error = exc_info.value
    # Should fail on both Rule 1 (prediction not found) and Rule 3 (count mismatch)
    assert len(error.reasons) >= 1
    combined = " ".join(error.reasons)
    assert "not exist" in combined or "does not match" in combined


# ---------------------------------------------------------------------------
# Test 7: Audit events logged correctly
# ---------------------------------------------------------------------------
def test_audit_logging(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    InferenceService._cached_model_id = None

    detection_id  = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result   = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)

    # Check for EXPLANATION_GENERATED and EXPLANATION_VALIDATED events
    audit_logs = db.scalars(
        select(AuditLog).where(
            AuditLog.action.in_([EVENT_GENERATED, EVENT_VALIDATED, EVENT_FAILED])
        ).order_by(AuditLog.timestamp.desc())
    ).all()
    actions = {log.action for log in audit_logs}

    assert EVENT_GENERATED in actions, f"Expected {EVENT_GENERATED} in {actions}"
    assert EVENT_VALIDATED  in actions, f"Expected {EVENT_VALIDATED} in {actions}"


# ---------------------------------------------------------------------------
# Test 8: Deterministic repeated explanations — same SHAP values both times
# ---------------------------------------------------------------------------
def test_deterministic_repeated_explanations(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    InferenceService._cached_model_id = None

    detection_id  = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result   = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)

    result1 = svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)
    result2 = svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)

    assert result1["shap_values"] == result2["shap_values"], (
        "SHAP values are not deterministic across repeated calls on the same input."
    )
    assert result1["base_value"] == result2["base_value"]
    assert result1["feature_importance"] == result2["feature_importance"]


# ---------------------------------------------------------------------------
# Test 9: Missing prediction_id raises FileNotFoundError
# ---------------------------------------------------------------------------
def test_missing_prediction_raises_not_found(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    non_existent_id = uuid4()
    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)

    with pytest.raises(FileNotFoundError, match="not found in database"):
        svc.explain_prediction(
            prediction_id=non_existent_id,
            feature_values=FEATURES,
        )


# ---------------------------------------------------------------------------
# Test 10: EXPLANATION_FAILED audit event is logged on failure
# ---------------------------------------------------------------------------
def test_explanation_failed_audit_logged(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    non_existent_id = uuid4()
    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)

    count_before = len(db.scalars(
        select(AuditLog).where(AuditLog.action == EVENT_FAILED)
    ).all())

    with pytest.raises(FileNotFoundError):
        svc.explain_prediction(prediction_id=non_existent_id, feature_values=FEATURES)

    count_after = len(db.scalars(
        select(AuditLog).where(AuditLog.action == EVENT_FAILED)
    ).all())

    assert count_after > count_before, (
        "EXPLANATION_FAILED audit event must be logged on missing prediction."
    )


# ---------------------------------------------------------------------------
# Test 11: Validator Rule 2 - model_id mismatch produces actionable error
# ---------------------------------------------------------------------------
def test_validator_model_id_mismatch(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    InferenceService._cached_model_id = None
    detection_id = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result  = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    validator = ExplanationValidator(db)
    shap_output = {
        "base_value":    0.3,
        "shap_values":   [0.1, 0.2, 0.3],
        "feature_names": list(FEATURES.keys()),
    }

    with pytest.raises(ExplanationValidationError) as exc_info:
        validator.validate(
            prediction_id=prediction_id,
            model_id=uuid4(),
            shap_output=shap_output,
        )

    reason_text = " ".join(exc_info.value.reasons)
    assert "does not match" in reason_text
    assert "active model may have changed" in reason_text or "original model" in reason_text


# ---------------------------------------------------------------------------
# Test 12: Validator Rule 4 - NaN SHAP value raises ExplanationValidationError
# ---------------------------------------------------------------------------
def test_validator_nan_shap_value(db: Session):
    db.rollback()
    validator = ExplanationValidator(db)

    shap_output = {
        "base_value":    0.3,
        "shap_values":   [0.1, float("nan"), 0.3],
        "feature_names": ["f1", "f2", "f3"],
    }

    with pytest.raises(ExplanationValidationError) as exc_info:
        validator.validate(
            prediction_id=uuid4(),
            model_id=uuid4(),
            shap_output=shap_output,
        )
    combined = " ".join(exc_info.value.reasons)
    assert "non-finite" in combined or "not exist" in combined


# ---------------------------------------------------------------------------
# Test 13: Wrong feature names raise ValueError before SHAP computation
# ---------------------------------------------------------------------------
def test_wrong_features_raises_value_error(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    InferenceService._cached_model_id = None
    detection_id = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result  = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    wrong_features = {"NonExistentFeature": 1.0, "AnotherBadFeature": 2.0}
    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)

    with pytest.raises(ValueError, match="Feature validation failed"):
        svc.explain_prediction(
            prediction_id=prediction_id,
            feature_values=wrong_features,
        )


# ---------------------------------------------------------------------------
# Test 14: Re-explanation is append-only - creates a new DB row each time
# ---------------------------------------------------------------------------
def test_re_explanation_creates_new_row(db: Session, env_setup):
    db.rollback()
    models_dir   = env_setup["models_dir"]
    datasets_dir = env_setup["datasets_dir"]

    InferenceService._cached_model_id = None
    detection_id = _make_detection(db)
    inf = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    pred_result  = inf.predict_raw(FEATURES, detection_id)
    prediction_id = UUID(pred_result["prediction_id"])

    svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)
    svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)
    svc.explain_prediction(prediction_id=prediction_id, feature_values=FEATURES)

    from app.repositories.explanation_repository import ExplanationRepository
    rows = ExplanationRepository(db).list_for_prediction(prediction_id)

    assert len(rows) >= 2, (
        "Expected at least 2 rows after two explain calls, got {}.".format(len(rows))
    )
    ids = [str(r.id) for r in rows]
    assert len(set(ids)) == len(ids), "Each explanation row must have a unique ID."
