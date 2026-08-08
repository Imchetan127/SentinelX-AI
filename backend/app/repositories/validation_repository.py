"""ValidationRepository — database access layer for ValidationResult rows."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.validation_result import ValidationResult
from app.repositories.base import BaseRepository


class ValidationRepository(BaseRepository[ValidationResult]):
    def __init__(self, session: Session):
        super().__init__(session, ValidationResult)

    def list_recent(self, limit: int = 50, offset: int = 0) -> List[ValidationResult]:
        """Return validation results ordered by most recent first."""
        stmt = (
            select(ValidationResult)
            .where(ValidationResult.is_deleted == False)
            .order_by(ValidationResult.validated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()

    def get_latest_for_model(self, model_id: str) -> Optional[ValidationResult]:
        """Return the most recent ValidationResult for a given model_id string."""
        try:
            model_uuid = UUID(model_id)
        except ValueError:
            return None
        stmt = (
            select(ValidationResult)
            .where(
                ValidationResult.model_id == model_uuid,
                ValidationResult.is_deleted == False,
            )
            .order_by(ValidationResult.validated_at.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def list_for_model(
        self,
        model_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ValidationResult]:
        """Return all ValidationResults for a given model_id, newest first."""
        try:
            model_uuid = UUID(model_id)
        except ValueError:
            return []
        stmt = (
            select(ValidationResult)
            .where(
                ValidationResult.model_id == model_uuid,
                ValidationResult.is_deleted == False,
            )
            .order_by(ValidationResult.validated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()
