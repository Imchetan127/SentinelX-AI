"""ExplanationRepository — database access layer for Explanation rows."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.explanation import Explanation
from app.repositories.base import BaseRepository


class ExplanationRepository(BaseRepository[Explanation]):
    def __init__(self, session: Session):
        super().__init__(session, Explanation)

    def get_latest_for_prediction(self, prediction_id: UUID) -> Optional[Explanation]:
        """Return the most recent Explanation for a given prediction_id."""
        stmt = (
            select(Explanation)
            .where(
                Explanation.prediction_id == prediction_id,
                Explanation.is_deleted == False,
            )
            .order_by(Explanation.explained_at.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def list_for_prediction(self, prediction_id: UUID) -> List[Explanation]:
        """Return all Explanation rows for a prediction, newest first."""
        stmt = (
            select(Explanation)
            .where(
                Explanation.prediction_id == prediction_id,
                Explanation.is_deleted == False,
            )
            .order_by(Explanation.explained_at.desc())
        )
        return self.session.scalars(stmt).all()

    def list_recent(self, limit: int = 50, offset: int = 0) -> List[Explanation]:
        """Return recent explanations ordered by most recent first."""
        stmt = (
            select(Explanation)
            .where(Explanation.is_deleted == False)
            .order_by(Explanation.explained_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.session.scalars(stmt).all()
