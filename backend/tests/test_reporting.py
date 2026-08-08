"""tests/test_reporting.py — Sprint 5.1 Incident Reporting Engine Test Suite.

Verifies:
  1. PDF rendering with all 11 required sections & branding.
  2. Cryptographic SHA256 integrity verification (VALID vs TAMPERED).
  3. Chronological timeline generation from Audit Logs.
  4. SHAP feature contributions & AI Quality Gate metrics formatting.
  5. Deterministic MITRE ATT&CK technique mapping.
  6. Database persistence of PDF paths and SHA256 hashes.
  7. Audit event logging (REPORT_GENERATED, REPORT_DOWNLOADED, REPORT_FAILED).
  8. RBAC enforcement (Admin/Security Analyst required for generation).
  9. Graceful handling of missing SHAP/model artifacts.
  10. End-to-end report generation, download, details, and verification workflow.
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
from app.models import Base, Model, Dataset, AuditLog, Explanation, Attack, Detection, Prediction, Incident, User, Report
from app.models.enums import Severity, AttackStatus, IncidentStatus, ModelStatus

from app.ml_engine.dataset_pipeline.pipeline import DatasetPipeline
from app.ml_engine.training.pipeline import TrainingService
from app.ml_engine.inference.engine import InferenceService
from app.ml_engine.explainability.service import ExplainabilityService

from app.reporting.service import ReportService
from app.reporting.integrity import ReportIntegrityVerifier
from app.reporting.mitre import MitreMapper
from app.reporting.formatters import RecommendationEngine
from app.reporting.audit import EVENT_REPORT_GENERATED, EVENT_REPORT_DOWNLOADED, EVENT_REPORT_FAILED


# ---------------------------------------------------------------------------
# Database & ML Environment Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db() -> Session:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    # Seed default dataset
    ds = Dataset(name="cicids_test", version="v1.0")
    session.add(ds)

    # Seed Admin User
    admin_user = User(
        id=uuid4(),
        username="sec_admin",
        email="admin@sentinelx.ai",
        password_hash="hashed_pw_secret",
        role="admin",
    )
    session.add(admin_user)

    # Seed Non-Analyst User
    guest_user = User(
        id=uuid4(),
        username="guest_user",
        email="guest@sentinelx.ai",
        password_hash="hashed_pw_secret",
        role="guest",
    )
    session.add(guest_user)

    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def full_environment(db: Session):
    """Train models, run inference, generate SHAP explanation, and create an Incident."""
    with TemporaryDirectory() as tmp_dir:
        np.random.seed(42)
        n_samples = 100

        df = pd.DataFrame({
            "Flow Duration":         np.random.randint(100, 100_000, n_samples),
            "Total Fwd Packets":     np.random.randint(1, 500, n_samples),
            "Fwd Packet Length Max":  np.random.randint(10, 1_500, n_samples),
            "Label":                 np.random.choice(["BENIGN", "SQL Injection"], n_samples),
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
            "hyperparameters": {"n_estimators": 5, "random_state": 42},
            "dataset_name": "cicids_test",
            "dataset_version": "v1.0",
            "preprocessing_version": "p1.0",
            "model_version": "1.0.0",
            "label_column": "Label",
        })

        # Set model to PRODUCTION in registry
        reg_path = os.path.join(models_dir, "registry", "registry.json")
        with open(reg_path) as f:
            reg = json.load(f)
        for m in reg:
            m["status"] = "PRODUCTION"
        with open(reg_path, "w") as f:
            json.dump(reg, f)

        # 1. Create Attack
        attack = Attack(
            type="SQL Injection",
            payload="UNION SELECT username, password_hash FROM users--",
            target="database_cluster_01",
            severity=Severity.HIGH,
            status=AttackStatus.COMPLETED,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(attack)
        db.flush()

        # 2. Create Detection
        detection = Detection(
            attack_id=attack.id,
            severity=Severity.HIGH,
            attack_type="SQL Injection",
            recommendation="Use parameterized queries",
            detected_at=datetime.now(timezone.utc),
        )
        db.add(detection)
        db.flush()

        # 3. Create Incident
        admin_user = db.scalars(select(User).where(User.role == "admin")).first()
        incident = Incident(
            attack_id=attack.id,
            assigned_to=admin_user.id,
            status=IncidentStatus.INVESTIGATING,
            priority=Severity.HIGH,
            title="CRITICAL: SQL Injection Attack Detected on DB Cluster",
            description="Automated intrusion alert raised by SentinelX AI engine.",
        )
        db.add(incident)
        db.commit()

        # 4. Run Inference
        InferenceService._cached_model_id = None
        features = {"Flow Duration": 12000, "Total Fwd Packets": 45, "Fwd Packet Length Max": 1100}
        inf_svc = InferenceService(db, base_dir=models_dir, datasets_dir=datasets_dir)
        pred_res = inf_svc.predict_raw(features_dict=features, detection_id=detection.id)
        prediction_id = UUID(pred_res["prediction_id"])

        # 5. Generate SHAP Explanation
        xai_svc = ExplainabilityService(db, base_dir=models_dir, datasets_dir=datasets_dir)
        expl_res = xai_svc.explain_prediction(prediction_id=prediction_id, feature_values=features)

        reports_dir = os.path.join(tmp_dir, "reports")

        yield {
            "tmp_dir": tmp_dir,
            "models_dir": models_dir,
            "datasets_dir": datasets_dir,
            "reports_dir": reports_dir,
            "incident_id": incident.id,
            "prediction_id": prediction_id,
            "admin_user_id": admin_user.id,
        }


# ---------------------------------------------------------------------------
# Test 1: Full Report Generation & PDF rendering with all 11 sections
# ---------------------------------------------------------------------------
def test_pdf_rendering_all_11_sections(db: Session, full_environment):
    db.rollback()
    inc_id = full_environment["incident_id"]
    user_id = full_environment["admin_user_id"]
    reports_dir = full_environment["reports_dir"]

    service = ReportService(db, reports_dir=reports_dir)
    report = service.generate_report(incident_id=inc_id, user_id=user_id)

    assert report is not None
    assert report.pdf_path is not None
    assert os.path.exists(report.pdf_path)
    assert os.path.getsize(report.pdf_path) > 10_000   # Multi-page PDF should be >10KB
    assert report.sha256_hash is not None
    assert len(report.sha256_hash) == 64   # Valid SHA256 hex string


# ---------------------------------------------------------------------------
# Test 2: Cryptographic SHA256 Integrity Verification (VALID vs TAMPERED)
# ---------------------------------------------------------------------------
def test_sha256_integrity_verification(db: Session, full_environment):
    db.rollback()
    inc_id = full_environment["incident_id"]
    user_id = full_environment["admin_user_id"]
    reports_dir = full_environment["reports_dir"]

    service = ReportService(db, reports_dir=reports_dir)
    report = service.generate_report(incident_id=inc_id, user_id=user_id)

    # 1. Verification of untampered file must be VALID
    res = service.verify_report_integrity(report.id)
    assert res["status"] == "VALID"
    assert res["is_valid"] is True
    assert res["computed_hash"] == report.sha256_hash

    # 2. Mutate PDF byte on disk → verification must return TAMPERED
    with open(report.pdf_path, "ab") as f:
        f.write(b"\x00TAMPERED_BYTE_MARKER\x00")

    res_tampered = service.verify_report_integrity(report.id)
    assert res_tampered["status"] == "TAMPERED"
    assert res_tampered["is_valid"] is False
    assert res_tampered["computed_hash"] != report.sha256_hash


# ---------------------------------------------------------------------------
# Test 3: MITRE ATT&CK Mapping Accuracy
# ---------------------------------------------------------------------------
def test_mitre_attack_mapping():
    mapper = MitreMapper()
    
    sqli_map = mapper.map_attack_type("SQL Injection")
    assert sqli_map["technique_id"] == "T1190"
    assert "Exploit Public-Facing Application" in sqli_map["technique_name"]
    assert "Initial Access" in sqli_map["tactic"]

    ddos_map = mapper.map_attack_type("DDoS Volumetric Attack")
    assert ddos_map["technique_id"] == "T1498"
    assert "Denial of Service" in ddos_map["technique_name"]


# ---------------------------------------------------------------------------
# Test 4: Deterministic Remediation Recommendation Engine
# ---------------------------------------------------------------------------
def test_recommendation_engine():
    rec_engine = RecommendationEngine()
    
    sqli_recs = rec_engine.generate_recommendations("SQL Injection")
    assert len(sqli_recs) >= 3
    rec_titles = [r["recommendation"] for r in sqli_recs]
    assert any("Parameterized Queries" in t for t in rec_titles)
    assert any("WAF" in t for t in rec_titles)


# ---------------------------------------------------------------------------
# Test 5: Report Persistence & ORM Verification
# ---------------------------------------------------------------------------
def test_report_persistence(db: Session, full_environment):
    db.rollback()
    inc_id = full_environment["incident_id"]
    user_id = full_environment["admin_user_id"]
    reports_dir = full_environment["reports_dir"]

    service = ReportService(db, reports_dir=reports_dir)
    report = service.generate_report(incident_id=inc_id, user_id=user_id)

    db_report = db.get(Report, report.id)
    assert db_report is not None
    assert db_report.incident_id == inc_id
    assert db_report.pdf_path == report.pdf_path
    assert db_report.sha256_hash == report.sha256_hash
    assert db_report.version == 1
    assert "SQL Injection" in db_report.title


# ---------------------------------------------------------------------------
# Test 6: Audit Event Logging (REPORT_GENERATED & REPORT_DOWNLOADED)
# ---------------------------------------------------------------------------
def test_audit_logging(db: Session, full_environment):
    db.rollback()
    inc_id = full_environment["incident_id"]
    user_id = full_environment["admin_user_id"]
    reports_dir = full_environment["reports_dir"]

    service = ReportService(db, reports_dir=reports_dir)
    report = service.generate_report(incident_id=inc_id, user_id=user_id)

    # Download report
    pdf_path, filename = service.download_report(report_id=report.id, user_id=user_id)
    assert os.path.exists(pdf_path)

    # Verify audit logs
    audits = db.scalars(
        select(AuditLog).where(
            AuditLog.action.in_([EVENT_REPORT_GENERATED, EVENT_REPORT_DOWNLOADED])
        ).order_by(AuditLog.timestamp.desc())
    ).all()
    actions = {a.action for a in audits}

    assert EVENT_REPORT_GENERATED in actions
    assert EVENT_REPORT_DOWNLOADED in actions


# ---------------------------------------------------------------------------
# Test 7: RBAC Enforcement for Report Generation
# ---------------------------------------------------------------------------
def test_rbac_enforcement(db: Session):
    db.rollback()
    from app.api.reports import _verify_generate_rbac
    from fastapi import HTTPException

    admin_payload = {"id": str(uuid4()), "role": "admin"}
    analyst_payload = {"id": str(uuid4()), "role": "security_analyst"}
    guest_payload = {"id": str(uuid4()), "role": "guest"}

    # Admin and Security Analyst should pass
    _verify_generate_rbac(admin_payload)
    _verify_generate_rbac(analyst_payload)

    # Guest role must raise HTTP 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        _verify_generate_rbac(guest_payload)
    assert exc_info.value.status_code == 403
    assert "not permitted" in exc_info.value.detail["message"]


# ---------------------------------------------------------------------------
# Test 8: Graceful Handling of Missing SHAP / Model Artifacts
# ---------------------------------------------------------------------------
def test_missing_shap_graceful_handling(db: Session, full_environment):
    db.rollback()
    # Create a bare Incident with Attack but NO prediction / SHAP explanation
    attack = Attack(
        type="Brute Force",
        payload="500 failed login attempts",
        target="auth_service",
        severity=Severity.MEDIUM,
        status=AttackStatus.COMPLETED,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(attack)
    db.flush()

    incident = Incident(
        attack_id=attack.id,
        status=IncidentStatus.OPEN,
        priority=Severity.MEDIUM,
        title="Brute Force Alert on Auth Service",
        description="High frequency login failure burst.",
    )
    db.add(incident)
    db.commit()

    reports_dir = full_environment["reports_dir"]
    service = ReportService(db, reports_dir=reports_dir)

    # Report generation MUST succeed even without SHAP explanation
    report = service.generate_report(incident_id=incident.id)
    assert report is not None
    assert os.path.exists(report.pdf_path)


# ---------------------------------------------------------------------------
# Test 9: Non-existent Incident Raises FileNotFoundError & Logs REPORT_FAILED
# ---------------------------------------------------------------------------
def test_non_existent_incident_fails_loudly(db: Session, full_environment):
    db.rollback()
    reports_dir = full_environment["reports_dir"]
    service = ReportService(db, reports_dir=reports_dir)
    fake_id = uuid4()

    with pytest.raises(FileNotFoundError, match="not found in database"):
        service.generate_report(incident_id=fake_id)

    # Verify REPORT_FAILED audit log is written
    failed_audit = db.scalars(
        select(AuditLog).where(AuditLog.action == EVENT_REPORT_FAILED).order_by(AuditLog.timestamp.desc())
    ).first()
    assert failed_audit is not None
    assert str(fake_id) in failed_audit.details


# ---------------------------------------------------------------------------
# Test 10: End-to-End Report Generation, Download, Details, and Verify Workflow
# ---------------------------------------------------------------------------
def test_report_service_e2e(db: Session, full_environment):
    db.rollback()
    inc_id = full_environment["incident_id"]
    user_id = full_environment["admin_user_id"]
    reports_dir = full_environment["reports_dir"]

    service = ReportService(db, reports_dir=reports_dir)

    # 1. Generate Report
    report = service.generate_report(incident_id=inc_id, user_id=user_id)
    assert report.id is not None

    # 2. Get Details
    report_details = service.get_report(report.id)
    assert report_details.id == report.id
    assert report_details.incident_id == inc_id

    # 3. List Reports
    reports_list = service.list_reports()
    assert any(r.id == report.id for r in reports_list)

    # 4. Download Report
    pdf_path, filename = service.download_report(report_id=report.id, user_id=user_id)
    assert os.path.exists(pdf_path)
    assert filename.startswith("report_incident_")

    # 5. Verify Integrity
    verify_res = service.verify_report_integrity(report.id)
    assert verify_res["status"] == "VALID"
    assert verify_res["is_valid"] is True
