from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.attack import Attack
from app.models.incident import Incident
from app.models.enums import IncidentStatus, Severity
from app.repositories.base import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    def __init__(self, session: Session):
        super().__init__(session, Incident)

    def get_by_analysis_result(self, analysis_result_id: UUID) -> Incident | None:
        from app.models.prediction import Prediction
        from app.models.detection import Detection
        statement = select(Incident).join(Attack).join(Detection).join(Prediction).where(
            Prediction.id == analysis_result_id,
            Incident.is_deleted == False
        )
        return self.session.scalars(statement).first()

    def count_by_status(self, status_list: List[str]) -> int:
        # Convert list of strings to IncidentStatus enums
        enum_list = []
        for s in status_list:
            try:
                enum_list.append(IncidentStatus[s.upper()])
            except KeyError:
                pass
        statement = select(func.count()).select_from(Incident).where(Incident.status.in_(enum_list), Incident.is_deleted == False)
        return int(self.session.scalar(statement) or 0)

    def list_open(self, limit: int = 100, offset: int = 0) -> List[Incident]:
        statement = select(Incident).where(Incident.is_deleted == False).limit(limit).offset(offset)
        return self.session.scalars(statement).all()

    def count_by_priority(self, priority: str) -> int:
        try:
            p_enum = Severity[priority.upper()]
        except KeyError:
            p_enum = Severity.MEDIUM
        statement = select(func.count()).select_from(Incident).where(Incident.priority == p_enum, Incident.is_deleted == False)
        return int(self.session.scalar(statement) or 0)
