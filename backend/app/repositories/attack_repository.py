from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.attack import Attack
from app.repositories.base import BaseRepository


class AttackRepository(BaseRepository[Attack]):
    def __init__(self, session: Session):
        super().__init__(session, Attack)

    def get_recent(self, limit: int = 5) -> List[Attack]:
        statement = select(Attack).order_by(desc(Attack.timestamp)).limit(limit)
        return self.session.scalars(statement).all()

    def get_by_user(self, user_id: UUID, limit: int = 100, offset: int = 0) -> List[Attack]:
        statement = select(Attack).where(Attack.created_by == user_id).limit(limit).offset(offset)
        return self.session.scalars(statement).all()
