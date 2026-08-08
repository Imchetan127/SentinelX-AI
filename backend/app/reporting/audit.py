"""app/reporting/audit.py — Audit Integration for Reporting Engine.

Logs immutable audit actions for report lifecycle events:
  - REPORT_GENERATED
  - REPORT_DOWNLOADED
  - REPORT_FAILED
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.audit_service import AuditService

logger = logging.getLogger("Reporting.Audit")

EVENT_REPORT_GENERATED  = "REPORT_GENERATED"
EVENT_REPORT_DOWNLOADED = "REPORT_DOWNLOADED"
EVENT_REPORT_FAILED     = "REPORT_FAILED"


class ReportAuditIntegration:
    """Emits immutable audit log entries for Report generation and downloads."""

    def __init__(self, db: Session):
        self._audit = AuditService(db)

    def log_generated(
        self,
        incident_id: UUID,
        report_id: UUID,
        sha256_hash: str,
        user_id: Optional[UUID] = None,
    ) -> None:
        self._audit.log_action(
            user_id=user_id,
            action=EVENT_REPORT_GENERATED,
            resource="Report",
            resource_id=report_id,
            ip_address="127.0.0.1",
            status="success",
            details=(
                f"Incident report generated for incident '{incident_id}'. "
                f"report_id={report_id}, sha256={sha256_hash[:16]}..."
            ),
        )

    def log_downloaded(
        self,
        report_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> None:
        self._audit.log_action(
            user_id=user_id,
            action=EVENT_REPORT_DOWNLOADED,
            resource="Report",
            resource_id=report_id,
            ip_address="127.0.0.1",
            status="success",
            details=f"Report PDF downloaded for report '{report_id}'.",
        )

    def log_failed(
        self,
        incident_id: Optional[UUID],
        reason: str,
        user_id: Optional[UUID] = None,
    ) -> None:
        self._audit.log_action(
            user_id=user_id,
            action=EVENT_REPORT_FAILED,
            resource="Report",
            resource_id=None,
            ip_address="127.0.0.1",
            status="failure",
            details=f"Report generation failed for incident '{incident_id}'. Reason: {reason}",
        )
