from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)

    def log_action(
        self,
        user_id: UUID | None,
        action: str,
        resource: str,
        resource_id: UUID | None,
        ip_address: str | None,
        status: str,
        details: str | None = None,
    ) -> AuditLog:
        # Append status and resource_id to details if present to keep information
        full_details = details or ""
        if status or resource_id:
            full_details += f" [Status: {status}]"
            if resource_id:
                full_details += f" [Resource ID: {resource_id}]"

        # Ensure user_id exists in database to prevent Foreign Key violations
        valid_user_id = None
        if user_id:
            try:
                from app.models.user import User
                existing_user = self.db.get(User, user_id)
                if existing_user:
                    valid_user_id = user_id
            except Exception:
                valid_user_id = None

        entry = AuditLog(
            user_id=valid_user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            details=full_details,
            timestamp=datetime.now(timezone.utc),
        )
        try:
            self.audit_repo.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            return entry
        except Exception:
            self.db.rollback()
            raise

    def list_recent_logs(self, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        return self.audit_repo.list_recent(limit=limit, offset=offset)

    def clear_logs(self) -> None:
        try:
            self.audit_repo.soft_delete_all()
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
