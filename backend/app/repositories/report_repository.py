from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: Session):
        super().__init__(session, Report)

    def get_by_incident(self, incident_id: UUID) -> List[Report]:
        statement = select(Report).where(Report.incident_id == incident_id, Report.is_deleted == False)
        return self.session.scalars(statement).all()
