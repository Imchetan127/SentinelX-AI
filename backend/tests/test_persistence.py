import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import SessionLocal, engine
from app.models import (
    Base,
    User,
    Dataset,
    Model,
    Attack,
    Detection,
    Prediction,
    Incident,
    Report,
    AuditLog,
)
from app.models.enums import Severity, AttackStatus, IncidentStatus, ModelStatus


@pytest.fixture(scope="module")
def db() -> Session:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL must be set for persistence tests")
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_database_connection(db: Session):
    result = db.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_user_crud_and_soft_delete(db: Session):
    user = User(
        username=f"testuser_{uuid4().hex[:8]}",
        email=f"test_{uuid4().hex[:8]}@example.com",
        password_hash="hash",
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    fetched = db.get(User, user.id)
    assert fetched is not None
    assert fetched.username == user.username

    fetched.is_deleted = True
    fetched.deleted_at = datetime.now(timezone.utc)
    db.add(fetched)
    db.commit()

    soft_deleted = db.get(User, user.id)
    assert soft_deleted.is_deleted is True
    assert soft_deleted.deleted_at is not None


def test_relationships_and_foreign_keys(db: Session):
    user = User(
        username=f"reluser_{uuid4().hex[:8]}",
        email=f"rel_{uuid4().hex[:8]}@example.com",
        password_hash="hash",
        role="analyst",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    attack = Attack(
        created_by=user.id,
        type="SQL Injection",
        payload="' OR 1=1",
        severity=Severity.HIGH,
        status=AttackStatus.COMPLETED,
        target="users_table",
        source_ip="192.168.1.100",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(attack)
    db.commit()
    db.refresh(attack)

    dataset = Dataset(
        name="cicids2017_test",
        version="v1.0",
        description="test dataset",
        source="localhost",
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    model = Model(
        dataset_id=dataset.id,
        created_by=user.id,
        algorithm="xgboost",
        version="v1",
        accuracy=0.92,
        precision=0.91,
        recall=0.9,
        f1_score=0.905,
        model_file="/tmp/model.bin",
        status=ModelStatus.VALIDATED,
        created_at=datetime.now(timezone.utc),
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    detection = Detection(
        attack_id=attack.id,
        severity=Severity.HIGH,
        attack_type="SQL Injection",
        recommendation="Apply input sanitization",
        detected_at=datetime.now(timezone.utc),
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)

    prediction = Prediction(
        detection_id=detection.id,
        model_id=model.id,
        prediction="malicious",
        confidence=0.98,
        probability=0.98,
        created_at=datetime.now(timezone.utc),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    incident = Incident(
        attack_id=attack.id,
        assigned_to=user.id,
        title="Investigate SQLi",
        description="Detected SQL injection attempt",
        priority=Severity.CRITICAL,
        status=IncidentStatus.OPEN,
        created_at=datetime.now(timezone.utc),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    report = Report(
        incident_id=incident.id,
        created_by=user.id,
        summary="Critical SQL Injection incident",
        recommendations="Apply parameter binding",
        version=1,
        created_at=datetime.now(timezone.utc),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Assert relationships
    assert attack.creator.id == user.id
    assert detection.attack.id == attack.id
    assert prediction.detection.id == detection.id
    assert prediction.model.id == model.id
    assert incident.attack.id == attack.id
    assert incident.assigned_user.id == user.id
    assert report.incident.id == incident.id
    assert report.creator.id == user.id


def test_audit_log_immutability(db: Session):
    log = AuditLog(
        user_id=None,
        action="login_attempt",
        resource="auth",
        ip_address="127.0.0.1",
        details="Anonymous login attempt",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    fetched = db.get(AuditLog, log.id)
    assert fetched is not None
    assert fetched.action == "login_attempt"


def test_dashboard_services_and_integration(db: Session):
    from app.services.analysis_service import AnalysisService
    from app.services.dashboard_service import DashboardService

    analysis_service = AnalysisService(db)
    dashboard_service = DashboardService(db)

    # 1. Clear database state or fetch starting metrics
    initial_metrics = dashboard_service.get_metrics()

    # 2. Record simulated inspection with CRITICAL threat detection
    res = analysis_service.record_blue_team_inspection(
        user_id=None,
        artifact_type="text",
        threat_detected=True,
        threat_category="SQL Injection Attack",
        risk_level="Critical",
        confidence=0.99,
        recommendations=["Enforce prepared statements"],
        payload="SELECT * FROM admin",
        source_ip="10.0.0.5"
    )

    assert res["attack_id"] is not None
    assert res["detection_id"] is not None
    assert res["prediction_id"] is not None
    assert res["incident_created"] is True

    # 3. Retrieve metrics and assert increments
    new_metrics = dashboard_service.get_metrics()
    assert new_metrics["total_threats_analyzed"] == initial_metrics["total_threats_analyzed"] + 1
    assert new_metrics["threats_detected"] == initial_metrics["threats_detected"] + 1
    assert new_metrics["active_incidents"] == initial_metrics["active_incidents"] + 1

    # Check distribution maps
    assert new_metrics["attack_severity_distribution"]["CRITICAL"] >= 1
    assert new_metrics["incident_status_distribution"]["OPEN"] >= 1

    # Check live audit log timeline has recorded events
    timeline = new_metrics["recent_activity_timeline"]
    assert len(timeline) > 0
    assert any("LAUNCH_ATTACK" in event["event"] for event in timeline)

