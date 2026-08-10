"""app/reporting/persistence.py — Database persistence for Report records."""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.report import Report
from app.repositories.report_repository import ReportRepository

logger = logging.getLogger("Reporting.Persistence")


class ReportPersistence:
    """Persists Report rows and handles transaction commits / rollbacks."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportRepository(db)

    def save_report(
        self,
        incident_id: UUID,
        pdf_path: str,
        sha256_hash: str,
        title: str,
        generated_by: Optional[UUID] = None,
        version: int = 1,
        summary: Optional[str] = None,
        recommendations: Optional[str] = None,
    ) -> Report:
        valid_user_id = None
        if generated_by:
            try:
                from app.models.user import User
                if self.db.get(User, generated_by):
                    valid_user_id = generated_by
            except Exception:
                valid_user_id = None

        report = Report(
            incident_id=incident_id,
            created_by=valid_user_id,
            pdf_path=pdf_path,
            sha256_hash=sha256_hash,
            title=title,
            version=version,
            summary=summary or title,
            recommendations=recommendations or pdf_path,
            created_at=datetime.now(timezone.utc),
        )

        try:
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            logger.info("ReportPersistence: saved report '%s' for incident '%s'.", report.id, incident_id)
            return report
        except Exception as exc:
            self.db.rollback()
            logger.error("Failed to persist report: %s", exc)
            raise
