from datetime import datetime, timezone
from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.prediction import Prediction
from app.models.detection import Detection
from app.models.enums import IncidentStatus, Severity
from app.repositories.incident_repository import IncidentRepository


class IncidentService:
    def __init__(self, db: Session):
        self.db = db
        self.incident_repo = IncidentRepository(db)

    def create_incident(
        self,
        analysis_result_id: UUID,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        status: str = "OPEN",
        assigned_user_id: UUID | None = None,
    ) -> Incident:
        pred = self.db.get(Prediction, analysis_result_id)
        if not pred:
            raise HTTPException(status_code=404, detail="Analysis result not found")
        det = self.db.get(Detection, pred.detection_id)
        if not det:
            raise HTTPException(status_code=404, detail="Detection not found")
        attack_id = det.attack_id

        try:
            priority_enum = Severity[priority.upper()]
        except KeyError:
            priority_enum = Severity.MEDIUM

        try:
            status_enum = IncidentStatus[status.upper()]
        except KeyError:
            status_enum = IncidentStatus.OPEN

        incident = Incident(
            attack_id=attack_id,
            assigned_to=assigned_user_id,
            title=title,
            description=description,
            priority=priority_enum,
            status=status_enum,
            created_at=datetime.now(timezone.utc),
        )
        try:
            self.incident_repo.add(incident)
            self.db.commit()
            self.db.refresh(incident)
            return incident
        except Exception:
            self.db.rollback()
            raise

    def get_incident(self, incident_id: UUID) -> Incident:
        return self.incident_repo.get(incident_id)

    def list_incidents(self, limit: int = 100, offset: int = 0) -> List[Incident]:
        return self.incident_repo.list(limit=limit, offset=offset)

    def count_open_incidents(self) -> int:
        return self.incident_repo.count_by_status(["OPEN", "INVESTIGATING"])

    def count_critical_incidents(self) -> int:
        return self.incident_repo.count_by_priority("critical")

    def close_incident(self, incident: Incident) -> Incident:
        incident.status = IncidentStatus.CLOSED
        # Instead of closed_at, we update TimestampMixin's deleted_at or updated_at, but we can set updated_at
        incident.updated_at = datetime.now(timezone.utc)
        try:
            self.incident_repo.session.add(incident)
            self.db.commit()
            self.db.refresh(incident)
            return incident
        except Exception:
            self.db.rollback()
            raise
