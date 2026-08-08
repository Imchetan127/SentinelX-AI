from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.report import Report
from app.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)

    def create_report(self, incident_id: UUID, generated_by: UUID | None, report_type: str, file_path: str) -> Report:
        report = Report(
            incident_id=incident_id,
            created_by=generated_by,
            summary=report_type,
            recommendations=file_path,
            version=1,
            created_at=datetime.now(timezone.utc),
        )
        try:
            self.report_repo.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception:
            self.db.rollback()
            raise

    def get_report(self, report_id: UUID) -> Report:
        return self.report_repo.get(report_id)

    def list_reports(self, limit: int = 100, offset: int = 0) -> List[Report]:
        return self.report_repo.list(limit=limit, offset=offset)

    def list_by_incident(self, incident_id: UUID) -> List[Report]:
        return self.report_repo.get_by_incident(incident_id)
