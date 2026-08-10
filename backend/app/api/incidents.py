from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin, get_current_user
from app.database.session import get_db
from app.schemas.incident import IncidentCreate, IncidentOut
from app.services.incident_service import IncidentService

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=IncidentOut)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    service = IncidentService(db)
    incident = service.create_incident(
        analysis_result_id=payload.analysis_result_id,
        assigned_user_id=payload.assigned_user_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=payload.status,
    )
    return incident


@router.get("", response_model=List[IncidentOut])
@router.get("/", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    service = IncidentService(db)
    return service.list_incidents()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: UUID, db: Session = Depends(get_db)):
    service = IncidentService(db)
    incident = service.get_incident(incident_id)
    if not incident or incident.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.post("/{incident_id}/close")
def close_incident(incident_id: UUID, current_user=Depends(get_current_admin), db: Session = Depends(get_db)):
    service = IncidentService(db)
    incident = service.get_incident(incident_id)
    if not incident or incident.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    service.close_incident(incident)
    return {"success": True, "message": "Incident closed"}


@router.get("/{incident_id}/timeline")
def get_incident_timeline(incident_id: UUID, db: Session = Depends(get_db)):
    """Retrieve timeline events linked to an incident via its root attack_id."""
    from app.models.incident import Incident
    from app.models.timeline_event import TimelineEvent
    from sqlalchemy import select

    incident = db.get(Incident, incident_id)
    if not incident or incident.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    events = db.scalars(
        select(TimelineEvent).where(TimelineEvent.attack_id == incident.attack_id).order_by(TimelineEvent.timestamp.asc())
    ).all()

    return {
        "success": True,
        "incident_id": str(incident.id),
        "attack_id": str(incident.attack_id),
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
