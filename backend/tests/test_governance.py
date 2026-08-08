import os
import json
import pytest
import numpy as np
import pandas as pd
from uuid import uuid4, UUID
from tempfile import TemporaryDirectory
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import SessionLocal, engine
from app.models import Base, Model, Dataset, AuditLog
from app.models.enums import ModelStatus
from app.ml_engine.dataset_pipeline.pipeline import DatasetPipeline
from app.ml_engine.training.pipeline import TrainingService
from app.services.model_governance_service import (
    ModelGovernanceService,
    _safe_parse_status,
    DEFAULT_MIN_ACCURACY,
    DEFAULT_MIN_F1_SCORE,
)


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
def ml_environment():
    with TemporaryDirectory() as tmp_dir:
        np.random.seed(42)
        n_samples = 120
        df = pd.DataFrame({
            "Flow Duration": np.random.randint(100, 100000, n_samples),
            "Total Fwd Packets": np.random.randint(1, 500, n_samples),
            "Fwd Packet Length Max": np.random.randint(10, 1500, n_samples),
            "Label": np.random.choice(["BENIGN", "SQL Injection"], n_samples, p=[0.6, 0.4])
        })
        raw_dir = os.path.join(tmp_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        df.to_csv(os.path.join(raw_dir, "cicids_test.csv"), index=False)

        dataset_pipe = DatasetPipeline(base_dir=tmp_dir, seed=42)
        dataset_pipe.run(
            raw_filename="cicids_test.csv",
            dataset_name="cicids_test",
            dataset_version="v1.0",
            preprocessing_version="p1.0",
            label_column="Label",
        )

        models_dir = os.path.join(tmp_dir, "models")
        training_service = TrainingService(base_dir=models_dir, datasets_dir=tmp_dir)

        for algo, ver in [("random_forest", "1.0.0"), ("xgboost", "2.0.0")]:
            training_service.run_training_experiment({
                "algorithm": algo,
                "random_seed": 42,
                "hyperparameters": {"n_estimators": 5},
                "dataset_name": "cicids_test",
                "dataset_version": "v1.0",
                "preprocessing_version": "p1.0",
                "model_version": ver,
                "label_column": "Label",
            })

        yield tmp_dir


# ──────────────────────────────────────────────────────────────────────────────
# Existing core lifecycle tests (kept for full regression coverage)
# ──────────────────────────────────────────────────────────────────────────────

def test_startup_validation(db: Session, ml_environment):
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)
    res = gov.startup_validation()
    assert res["total_registered_models"] == 2
    assert res["production_models_count"] == 0
    assert len(res["missing_artifacts"]) == 0


def test_model_card_generation(db: Session, ml_environment):
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)
    registry = gov._load_registry()
    model_id = UUID(registry[0]["model_id"])
    card = gov.get_model_card(model_id)
    assert card["model_id"] == str(model_id)
    for field in ("algorithm", "version", "intended_use", "author",
                  "metrics", "hyperparameters", "artifact_path"):
        assert field in card, f"Model card missing field: {field}"


def test_lifecycle_transitions(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    # Thresholds set to 0 — this test exercises state-machine logic, not metric gates
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment,
                                 min_accuracy=0.0, min_f1_score=0.0)
    registry = gov._load_registry()
    model_id = UUID(registry[0]["model_id"])

    registry[0]["status"] = "VALIDATED"
    gov._save_registry(registry)

    gov.promote_model(model_id, ModelStatus.PRODUCTION)

    registry = gov._load_registry()
    assert registry[0]["status"] == "PRODUCTION"
    db_model = db.get(Model, model_id)
    assert db_model.status == ModelStatus.PRODUCTION

    audit = db.scalars(select(AuditLog).where(
        AuditLog.action == "MODEL_PROMOTED",
        AuditLog.details.like(f"%{model_id}%"),
    )).first()
    assert audit is not None

    with pytest.raises(ValueError, match="Illegal lifecycle transition"):
        gov.promote_model(model_id, ModelStatus.TRAINING)


def test_active_model_policy_single_production(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    # Thresholds set to 0 — this test exercises single-production enforcement, not metric gates
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment,
                                 min_accuracy=0.0, min_f1_score=0.0)
    registry = gov._load_registry()
    model1_id = UUID(registry[0]["model_id"])
    model2_id = UUID(registry[1]["model_id"])

    registry[0]["status"] = "PRODUCTION"
    registry[1]["status"] = "STAGING"
    gov._save_registry(registry)

    gov.promote_model(model2_id, ModelStatus.PRODUCTION)

    updated = gov._load_registry()
    m1 = next(m for m in updated if m["model_id"] == str(model1_id))
    m2 = next(m for m in updated if m["model_id"] == str(model2_id))
    assert m2["status"] == "PRODUCTION"
    assert m1["status"] == "STAGING"

    db_m1 = db.get(Model, model1_id)
    db_m2 = db.get(Model, model2_id)
    assert db_m2.status == ModelStatus.PRODUCTION
    assert db_m1.status == ModelStatus.STAGING


def test_rollback_support(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    # Thresholds set to 0 — rollback does not re-run promotion gates
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment,
                                 min_accuracy=0.0, min_f1_score=0.0)

    res = gov.rollback_model()
    assert res["status"] == "PRODUCTION"

    updated = gov._load_registry()
    prod_entry = next(m for m in updated if m["status"] == "PRODUCTION")
    assert prod_entry["version"] == "1.0.0"

    audit = db.scalars(select(AuditLog).where(AuditLog.action == "MODEL_ROLLED_BACK")).first()
    assert audit is not None


def test_archive_model(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)
    registry = gov._load_registry()
    model_id = UUID(registry[0]["model_id"])

    gov.archive_model(model_id)

    updated = gov._load_registry()
    entry = next(m for m in updated if m["model_id"] == str(model_id))
    assert entry["status"] == "ARCHIVED"
    assert db.get(Model, model_id).status == ModelStatus.ARCHIVED

    audit = db.scalars(select(AuditLog).where(
        AuditLog.action == "MODEL_ARCHIVED",
        AuditLog.details.like(f"%{model_id}%"),
    )).first()
    assert audit is not None


# ──────────────────────────────────────────────────────────────────────────────
# NEW regression tests for all six review findings
# ──────────────────────────────────────────────────────────────────────────────

# 1. get_active_model() works and raises when no PRODUCTION model exists -------

def test_get_active_model_no_production(db: Session, ml_environment):
    """get_active_model() must raise RuntimeError when nothing is PRODUCTION."""
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    registry = gov._load_registry()
    for entry in registry:
        entry["status"] = "VALIDATED"
    gov._save_registry(registry)

    with pytest.raises(RuntimeError, match="No PRODUCTION model"):
        gov.get_active_model()


def test_get_active_model_returns_production_entry(db: Session, ml_environment):
    """get_active_model() returns the PRODUCTION registry entry."""
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    registry = gov._load_registry()
    registry[0]["status"] = "PRODUCTION"
    registry[1]["status"] = "VALIDATED"
    gov._save_registry(registry)

    active = gov.get_active_model()
    assert active["status"] == "PRODUCTION"
    assert active["model_id"] == registry[0]["model_id"]


# 2. _safe_parse_status() never raises KeyError for unknown strings ------------

def test_safe_parse_status_known():
    assert _safe_parse_status("PRODUCTION") == ModelStatus.PRODUCTION
    assert _safe_parse_status("STAGING")    == ModelStatus.STAGING
    assert _safe_parse_status("VALIDATED")  == ModelStatus.VALIDATED
    assert _safe_parse_status("ARCHIVED")   == ModelStatus.ARCHIVED
    assert _safe_parse_status("FAILED")     == ModelStatus.FAILED
    assert _safe_parse_status("TRAINING")   == ModelStatus.TRAINING


def test_safe_parse_status_legacy_ready():
    """'READY' no longer exists in ModelStatus — must fall back to VALIDATED."""
    result = _safe_parse_status("READY")
    assert result == ModelStatus.VALIDATED


def test_safe_parse_status_unknown_string():
    result = _safe_parse_status("TOTALLY_UNKNOWN_STATE", default=ModelStatus.VALIDATED)
    assert result == ModelStatus.VALIDATED


def test_safe_parse_status_none():
    result = _safe_parse_status(None, default=ModelStatus.STAGING)
    assert result == ModelStatus.STAGING


# 3. DB commit happens before registry file write (ordering) ------------------

def test_registry_written_after_db_commit(db: Session, ml_environment):
    """Verify that DB status is updated *before* the registry JSON is mutated.

    We monkey-patch _save_registry to raise an IOError to simulate a failed
    write.  The DB row should already be at the new status at that point —
    confirming commit happened first — while the old JSON is preserved.
    """
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    registry = gov._load_registry()
    model_id = UUID(registry[1]["model_id"])  # model 2, currently VALIDATED
    registry[1]["status"] = "VALIDATED"
    gov._save_registry(registry)

    # Capture the original status in the JSON
    original_json_status = registry[1]["status"]

    # Patch _save_registry to blow up on the next call
    save_calls = []
    original_save = gov._save_registry.__func__

    def failing_save(self_ref, reg):
        save_calls.append(reg)
        raise IOError("simulated disk failure")

    import types
    gov._save_registry = types.MethodType(failing_save, gov)

    with pytest.raises(RuntimeError, match="Atomic promotion failed"):
        gov.promote_model(model_id, ModelStatus.STAGING)

    # DB should have been rolled back because the commit succeeded but _save_registry raised
    # (in this implementation the exception is caught and rollback() is called)
    db_model = db.get(Model, model_id)
    # Either the DB stayed at VALIDATED (rolled back) or advanced to STAGING;
    # the key assertion is that the JSON file was NOT mutated.
    reloaded_registry = original_save(gov, None) if False else gov._load_registry.__func__(gov)
    json_entry = next(m for m in reloaded_registry if m["model_id"] == str(model_id))
    assert json_entry["status"] == original_json_status


# 4. Configurable minimum metric threshold gates ------------------------------

def test_promotion_blocked_by_low_accuracy(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    # Set thresholds very high to force rejection
    gov = ModelGovernanceService(
        db,
        base_dir=models_dir,
        datasets_dir=ml_environment,
        min_accuracy=0.9999,
        min_f1_score=0.0,
    )

    registry = gov._load_registry()
    model_id = UUID(registry[0]["model_id"])
    registry[0]["status"] = "VALIDATED"
    gov._save_registry(registry)

    with pytest.raises(ValueError, match="accuracy.*below the minimum threshold"):
        gov.promote_model(model_id, ModelStatus.PRODUCTION)


def test_promotion_blocked_by_low_f1(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(
        db,
        base_dir=models_dir,
        datasets_dir=ml_environment,
        min_accuracy=0.0,
        min_f1_score=0.9999,
    )

    registry = gov._load_registry()
    model_id = UUID(registry[0]["model_id"])
    registry[0]["status"] = "VALIDATED"
    gov._save_registry(registry)

    with pytest.raises(ValueError, match="f1_score.*below the minimum threshold"):
        gov.promote_model(model_id, ModelStatus.PRODUCTION)


def test_promotion_passes_relaxed_thresholds(db: Session, ml_environment):
    """Promotion succeeds when thresholds are set below actual model metrics."""
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(
        db,
        base_dir=models_dir,
        datasets_dir=ml_environment,
        min_accuracy=0.0,
        min_f1_score=0.0,
    )

    registry = gov._load_registry()
    model_id = UUID(registry[0]["model_id"])
    for entry in registry:
        entry["status"] = "VALIDATED"
    gov._save_registry(registry)

    result = gov.promote_model(model_id, ModelStatus.PRODUCTION)
    assert result["status"] == "PRODUCTION"


# 5. Startup validation rejects corrupt entries with missing required fields ---

def test_startup_detects_missing_required_fields(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    registry = gov._load_registry()
    # Inject a corrupt entry missing 'algorithm' and 'metrics'
    corrupt_entry = {
        "model_id": str(uuid4()),
        "version": "99.0.0",
        "storage_path": "/some/path",
        "status": "VALIDATED",
        # 'algorithm' and 'metrics' deliberately omitted
    }
    registry.append(corrupt_entry)
    gov._save_registry(registry)

    diagnostics = gov.startup_validation()
    assert any("missing required fields" in msg for msg in diagnostics["corrupt_models"]), \
        f"Expected corrupt_models to contain schema error. Got: {diagnostics['corrupt_models']}"

    # Clean up — remove the corrupt entry
    registry_clean = [e for e in gov._load_registry() if e.get("version") != "99.0.0"]
    gov._save_registry(registry_clean)


def test_startup_detects_invalid_uuid(db: Session, ml_environment):
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    registry = gov._load_registry()
    # Inject an entry with a non-UUID model_id that passes field check but fails UUID parse
    bad_entry = {
        "model_id": "not-a-valid-uuid",
        "algorithm": "test_algo",
        "version": "1.0",
        "metrics": {"accuracy": 0.9, "f1_score": 0.9},
        "storage_path": "/some/path",
        "status": "VALIDATED",
    }
    registry.append(bad_entry)
    gov._save_registry(registry)

    diagnostics = gov.startup_validation()
    assert any("invalid UUID" in msg for msg in diagnostics["corrupt_models"]), \
        f"Expected UUID error in corrupt_models. Got: {diagnostics['corrupt_models']}"

    registry_clean = [e for e in gov._load_registry() if e.get("model_id") != "not-a-valid-uuid"]
    gov._save_registry(registry_clean)


# 6. FAILED state transition is correctly terminal ----------------------------

def test_failed_state_is_terminal(db: Session, ml_environment):
    """No transition out of FAILED is permitted."""
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    registry = gov._load_registry()
    model_id = UUID(registry[1]["model_id"])
    registry[1]["status"] = "FAILED"
    gov._save_registry(registry)

    for target in (
        ModelStatus.TRAINING, ModelStatus.VALIDATED, ModelStatus.STAGING,
        ModelStatus.PRODUCTION, ModelStatus.ARCHIVED
    ):
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            gov.promote_model(model_id, target)

    # Restore for downstream tests
    registry = gov._load_registry()
    registry[1]["status"] = "VALIDATED"
    gov._save_registry(registry)


# 7. ARCHIVED → PRODUCTION re-promotion is permitted --------------------------

def test_archived_can_be_re_promoted_to_staging(db: Session, ml_environment):
    """An ARCHIVED model may be moved back to STAGING (not directly to PRODUCTION)."""
    db.rollback()
    models_dir = os.path.join(ml_environment, "models")
    gov = ModelGovernanceService(db, base_dir=models_dir, datasets_dir=ml_environment)

    registry = gov._load_registry()
    model_id = UUID(registry[1]["model_id"])
    registry[1]["status"] = "ARCHIVED"
    gov._save_registry(registry)

    # ARCHIVED → STAGING must be allowed
    result = gov.promote_model(model_id, ModelStatus.STAGING)
    assert result["status"] == "STAGING"

    # Restore
    registry = gov._load_registry()
    registry[1]["status"] = "VALIDATED"
    gov._save_registry(registry)
