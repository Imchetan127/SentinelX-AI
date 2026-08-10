import pytest
from datetime import datetime, timezone
from uuid import uuid4, UUID
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.attack import Attack
from app.models.detection import Detection
from app.models.prediction import Prediction
from app.models.explanation import Explanation
from app.models.mitigation import Mitigation
from app.models.incident import Incident
from app.models.timeline_event import TimelineEvent
from app.models.model import Model
from app.models.enums import Severity, AttackStatus, IncidentStatus, ModelStatus
from app.services.event_pipeline_service import EventPipelineService, THREAT_BLOCK_THRESHOLD
from app.services.attack_service import AttackService
from app.services.report_service import ReportService
from app.red_team.generator import red_team_generator


# -----------------------------------------------------------------------------
# 1. END-TO-END PIPELINE TESTS
# -----------------------------------------------------------------------------

def test_e2e_attack_simulation_pipeline_above_threshold(db: Session):
    """
    End-to-End Test: Above-Threshold Attack Simulation (SQLi Auth Bypass)
    Asserts complete chain: Attack -> Detection -> Multi-Model -> SHAP -> Mitigation -> Incident -> Timeline -> Report
    """
    # 1. Create Attack simulation record
    attack_service = AttackService(db)
    vector = red_team_generator.simulate_attack("SIM-SQLI-02")["vector_details"]
    
    attack = attack_service.create_attack(
        user_id=None,
        attack_type=vector["name"],
        payload=str(vector["payload"]),
        target="system",
        severity=vector["risk_level"].lower(),
        status="completed",
        source_ip="192.168.1.100"
    )
    attack_id = attack.id

    # 2. Trigger Event Pipeline
    pipeline_service = EventPipelineService(db)
    result = pipeline_service.process_attack(attack_id=attack_id)

    # 3. Assert Correlation ID structure
    assert result["attack_id"] == str(attack_id)
    assert result["detection_id"] is not None
    assert result["explanation_id"] is not None
    assert result["mitigation_id"] is not None
    assert result["incident_id"] is not None
    assert result["incident_created"] is True
    assert result["consensus_threat_score"] >= (THREAT_BLOCK_THRESHOLD * 100)
    assert result["recommended_action"] == "BLOCK"
    assert result["action_taken"] == "WAF_RULE_BLOCK"

    # 4. Assert Detection & Predictions in DB
    detection = db.get(Detection, UUID(result["detection_id"]))
    assert detection is not None
    assert detection.attack_id == attack_id
    assert detection.severity in [Severity.HIGH, Severity.CRITICAL]

    predictions = db.scalars(select(Prediction).where(Prediction.detection_id == detection.id)).all()
    assert len(predictions) > 0
    for p in predictions:
        assert p.prediction in ["malicious", "clean", "unavailable"]
        assert 0.0 <= p.confidence <= 1.0

    # 5. Assert SHAP Explanation in DB
    explanation = db.get(Explanation, UUID(result["explanation_id"]))
    assert explanation is not None
    assert len(explanation.feature_names) > 0
    assert len(explanation.top_positive_contributors) > 0

    # 6. Assert Mitigation in DB
    mitigation = db.get(Mitigation, UUID(result["mitigation_id"]))
    assert mitigation is not None
    assert mitigation.attack_id == attack_id
    assert mitigation.recommended_action == "BLOCK"
    assert mitigation.action_taken == "WAF_RULE_BLOCK"
    assert "WAF Rule #" in mitigation.rule_applied

    # 7. Assert Incident Auto-Creation in DB
    incident = db.get(Incident, UUID(result["incident_id"]))
    assert incident is not None
    assert incident.attack_id == attack_id
    assert incident.status == IncidentStatus.OPEN
    assert incident.priority in [Severity.HIGH, Severity.CRITICAL]

    # 8. Assert Append-Only Timeline Events Chain
    timeline_events = db.scalars(
        select(TimelineEvent).where(TimelineEvent.attack_id == attack_id).order_by(TimelineEvent.timestamp.asc())
    ).all()

    assert len(timeline_events) == 5
    stages = [e.stage for e in timeline_events]
    assert stages == ["RED_TEAM", "AI_ENGINE", "XAI_ENGINE", "BLUE_TEAM", "INCIDENT"]
    
    # Assert chronological ordering
    for i in range(len(timeline_events) - 1):
        assert timeline_events[i].timestamp <= timeline_events[i + 1].timestamp
        assert timeline_events[i].attack_id == attack_id

    # 9. Assert PDF Report Generation from Incident
    from app.reporting.service import ReportService as PDFReportService
    report_service = PDFReportService(db)
    report = report_service.generate_report(incident_id=incident.id, user_id=None)
    assert report is not None
    assert report.incident_id == incident.id
    assert report.sha256_hash is not None
    assert len(report.sha256_hash) == 64


def test_e2e_attack_simulation_pipeline_sub_threshold(db: Session):
    """
    End-to-End Test: Sub-Threshold Payload (Clean Telemetry)
    Asserts pipeline completes, WAF logs passthrough, and NO Incident is created.
    """
    attack_service = AttackService(db)
    attack = attack_service.create_attack(
        user_id=None,
        attack_type="Benign System Ping",
        payload="GET /api/v1/health HTTP/1.1",
        target="system",
        severity="low",
        status="completed",
        source_ip="10.0.0.1"
    )

    pipeline_service = EventPipelineService(db)
    result = pipeline_service.process_attack(attack_id=attack.id)

    assert result["attack_id"] == str(attack.id)
    assert result["incident_created"] is False
    assert result["incident_id"] is None
    assert result["recommended_action"] == "MONITOR"
    assert result["action_taken"] == "PASSTHROUGH_LOGGED"

    # Assert NO incident row in DB
    incident = db.scalars(select(Incident).where(Incident.attack_id == attack.id)).first()
    assert incident is None

    # Assert timeline ends at BLUE_TEAM stage without INCIDENT stage
    timeline_events = db.scalars(
        select(TimelineEvent).where(TimelineEvent.attack_id == attack.id).order_by(TimelineEvent.timestamp.asc())
    ).all()
    stages = [e.stage for e in timeline_events]
    assert "INCIDENT" not in stages
    assert stages[-1] == "BLUE_TEAM"


# -----------------------------------------------------------------------------
# 2. FAILURE-PATH & RESILIENCE TESTS
# -----------------------------------------------------------------------------

def test_failure_path_partial_model_unavailability(db: Session):
    """
    Failure Path Test: Partial Model Failure
    Mocks one model with status FAILED. Asserts FAILED model returns "unavailable",
    while available models return real predictions, and consensus calculates cleanly.
    """
    from app.models.dataset import Dataset
    ds = Dataset(name="test_ds", version="v1")
    db.add(ds)
    db.flush()

    m_ok = Model(dataset_id=ds.id, algorithm="xgboost", version="v1.0", accuracy=0.98, model_file="xgboost.bin", status=ModelStatus.PRODUCTION)
    m_fail = Model(dataset_id=ds.id, algorithm="random_forest", version="v1.0", accuracy=0.00, model_file="rf.bin", status=ModelStatus.FAILED)
    db.add_all([m_ok, m_fail])
    db.flush()

    attack_service = AttackService(db)
    attack = attack_service.create_attack(
        user_id=None,
        attack_type="SQL Injection",
        payload="SELECT * FROM users WHERE '1'='1'",
        target="system",
        severity="high",
        status="completed"
    )

    pipeline_service = EventPipelineService(db)
    result = pipeline_service.process_attack(attack.id)

    assert result["success"] if "success" in result else True
    detection_id = UUID(result["detection_id"])
    predictions = db.scalars(select(Prediction).where(Prediction.detection_id == detection_id)).all()

    statuses = {p.model_id: p.prediction for p in predictions}
    assert statuses[m_fail.id] == "unavailable"
    assert statuses[m_ok.id] in ["malicious", "clean"]


def test_failure_path_unknown_attack_type():
    """
    Failure Path Test: Unknown Attack Vector ID
    Invoking simulate_attack with invalid vector_id raises KeyError / ValueError.
    """
    with pytest.raises(ValueError, match="Unknown attack vector"):
        red_team_generator.simulate_attack("non_existent_vector_9999")


def test_duplicate_attack_submission_idempotency(db: Session):
    """
    Idempotency Test: Duplicate Attack Submissions
    Documents chosen architecture: Each simulation run creates a unique root correlation ID (Attack.id).
    Submitting duplicate attacks generates distinct attack events with separate correlation chains.
    """
    attack_service = AttackService(db)
    atk1 = attack_service.create_attack(user_id=None, attack_type="XSS Script", payload="<script>alert(1)</script>", severity="medium")
    atk2 = attack_service.create_attack(user_id=None, attack_type="XSS Script", payload="<script>alert(1)</script>", severity="medium")

    assert atk1.id != atk2.id

    pipe = EventPipelineService(db)
    res1 = pipe.process_attack(atk1.id)
    res2 = pipe.process_attack(atk2.id)

    assert res1["attack_id"] != res2["attack_id"]
    assert res1["detection_id"] != res2["detection_id"]
