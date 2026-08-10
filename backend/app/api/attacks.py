from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.schemas.attack import AttackCreate, AttackOut
from app.services.attack_service import AttackService

router = APIRouter(
    prefix="/attacks",
    tags=["Attack Events"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=AttackOut)
def create_attack(payload: AttackCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AttackService(db)
    attack = service.create_attack(
        user_id=current_user["id"],
        attack_type=payload.attack_type,
        payload=payload.payload,
        target=payload.target,
        severity=payload.severity,
        status=payload.status,
        source_ip=payload.source_ip,
    )
    return attack


@router.get("/", response_model=List[AttackOut])
def list_attacks(db: Session = Depends(get_db)):
    service = AttackService(db)
    return service.list_attacks()


@router.get("/{attack_id}", response_model=AttackOut)
def get_attack(attack_id: UUID, db: Session = Depends(get_db)):
    service = AttackService(db)
    attack = service.get_attack(attack_id)
    if not attack or attack.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attack record not found")
    return attack


@router.delete("/{attack_id}")
def delete_attack(attack_id: UUID, db: Session = Depends(get_db)):
    service = AttackService(db)
    attack = service.get_attack(attack_id)
    if not attack or attack.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attack record not found")
    service.soft_delete_attack(attack)
    return {"success": True, "message": "Attack soft deleted"}


@router.get("/{attack_id}/status")
def get_attack_pipeline_status(attack_id: UUID, db: Session = Depends(get_db)):
    """Lightweight status polling endpoint returning current pipeline state."""
    from app.models.attack import Attack
    from app.models.detection import Detection
    from app.models.mitigation import Mitigation
    from app.models.incident import Incident
    from app.models.timeline_event import TimelineEvent
    from sqlalchemy import select

    attack = db.get(Attack, attack_id)
    if not attack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Attack '{attack_id}' not found")

    detection = db.scalars(select(Detection).where(Detection.attack_id == attack.id)).first()
    mitigation = db.scalars(select(Mitigation).where(Mitigation.attack_id == attack.id)).first()
    incident = db.scalars(select(Incident).where(Incident.attack_id == attack.id)).first()
    events = db.scalars(select(TimelineEvent).where(TimelineEvent.attack_id == attack.id).order_by(TimelineEvent.timestamp.asc())).all()

    return {
        "success": True,
        "attack_id": str(attack.id),
        "attack_type": attack.type,
        "severity": attack.severity.value,
        "status": attack.status.value,
        "detection_status": "completed" if detection else "pending",
        "detection_id": str(detection.id) if detection else None,
        "mitigation_status": mitigation.status if mitigation else "none",
        "action_taken": mitigation.action_taken if mitigation else "none",
        "incident_created": incident is not None,
        "incident_id": str(incident.id) if incident else None,
        "timeline_count": len(events),
        "latest_stage": events[-1].stage if events else "RED_TEAM"
    }


@router.get("/{attack_id}/detection")
def get_attack_detection(attack_id: UUID, db: Session = Depends(get_db)):
    """Retrieve full detection, multi-model predictions, and mitigation for an attack."""
    from app.models.detection import Detection
    from app.models.prediction import Prediction
    from app.models.mitigation import Mitigation
    from sqlalchemy import select

    detection = db.scalars(select(Detection).where(Detection.attack_id == attack_id)).first()
    if not detection:
        return {
            "success": False,
            "status": "unavailable",
            "message": f"No detection record found for attack '{attack_id}'."
        }

    from app.models.model import Model
    all_models = db.scalars(select(Model).where(Model.is_deleted == False)).all()
    predictions = db.scalars(select(Prediction).where(Prediction.detection_id == detection.id)).all()
    mitigation = db.scalars(select(Mitigation).where(Mitigation.detection_id == detection.id)).first()

    pred_map = {p.model_id: p for p in predictions}
    prediction_items = []

    for m in all_models:
        p = pred_map.get(m.id)
        algo_name = m.algorithm.replace("_", " ").title() if m.algorithm else "Custom Model"
        if p:
            prediction_items.append({
                "id": str(p.id),
                "model_id": str(m.id),
                "algorithm": m.algorithm,
                "model_name": algo_name,
                "prediction": p.prediction,
                "confidence": p.confidence if p.prediction != "unavailable" else None,
                "probability": p.probability if p.prediction != "unavailable" else None,
                "status": "active" if p.prediction != "unavailable" else "unavailable",
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
        else:
            prediction_items.append({
                "id": None,
                "model_id": str(m.id),
                "algorithm": m.algorithm,
                "model_name": algo_name,
                "prediction": "unavailable",
                "confidence": None,
                "probability": None,
                "status": "unavailable",
                "reason": "Model not invoked for this detection event"
            })

    return {
        "success": True,
        "status": "completed",
        "data": {
            "id": str(detection.id),
            "attack_id": str(detection.attack_id),
            "severity": detection.severity.value,
            "attack_type": detection.attack_type,
            "recommendation": detection.recommendation,
            "detected_at": detection.detected_at.isoformat(),
            "predictions": prediction_items,
            "mitigation": {
                "id": str(mitigation.id),
                "recommended_action": mitigation.recommended_action,
                "action_taken": mitigation.action_taken,
                "rule_applied": mitigation.rule_applied,
                "status": mitigation.status
            } if mitigation else None
        }
    }


@router.get("/{attack_id}/timeline")
def get_attack_timeline(attack_id: UUID, db: Session = Depends(get_db)):
    """Retrieve append-only timeline events for an attack simulation."""
    from app.models.timeline_event import TimelineEvent
    from sqlalchemy import select

    events = db.scalars(
        select(TimelineEvent).where(TimelineEvent.attack_id == attack_id).order_by(TimelineEvent.timestamp.asc())
    ).all()

    return {
        "success": True,
        "attack_id": str(attack_id),
        "count": len(events),
        "events": [
            {
                "id": str(e.id),
                "stage": e.stage,
                "title": e.title,
                "details": e.details,
                "severity": e.severity,
                "timestamp": e.timestamp.isoformat()
            }
            for e in events
        ]
    }
