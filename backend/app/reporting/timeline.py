"""app/reporting/timeline.py — Incident Timeline builder using immutable Audit Logs."""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger("Reporting.TimelineBuilder")


class TimelineBuilder:
    """Constructs a chronological timeline of security events from Audit Logs."""

    def __init__(self, db: Session):
        self.db = db

    def build_timeline(
        self,
        incident_id: str,
        attack_id: str,
        prediction_id: Optional[str] = None,
        explanation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query audit logs matching incident/attack/prediction/explanation IDs."""
        stmt = select(AuditLog).order_by(AuditLog.timestamp.asc())
        all_logs = self.db.scalars(stmt).all()

        timeline_events = []
        target_ids = {i for i in [incident_id, attack_id, prediction_id, explanation_id] if i and i != "N/A"}

        for log in all_logs:
            details_str = log.details or ""
            # Match by target UUIDs or key action keywords
            matched = any(tid in details_str for tid in target_ids)
            
            if matched or log.action in (
                "ATTACK_CREATED", "DETECTION_TRIGGERED",
                "PREDICTION_EXECUTED", "EXPLANATION_GENERATED",
                "INCIDENT_RAISED", "INCIDENT_STATUS_UPDATED",
                "MODEL_PROMOTED", "MODEL_LOADED"
            ):
                timeline_events.append({
                    "id": str(log.id),
                    "timestamp": log.timestamp.isoformat() if log.timestamp else "N/A",
                    "action": log.action,
                    "resource": log.resource,
                    "details": details_str,
                    "user_id": str(log.user_id) if log.user_id else "System",
                })

        logger.info("TimelineBuilder: constructed %d timeline events.", len(timeline_events))
        return timeline_events
