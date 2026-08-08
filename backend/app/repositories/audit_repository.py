from typing import List
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: Session):
        super().__init__(session, AuditLog)

    def list_recent(self, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        statement = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit).offset(offset)
        return self.session.scalars(statement).all()

    def soft_delete_all(self) -> None:
        # Audit logs are immutable - no-op to comply with specs
        pass
