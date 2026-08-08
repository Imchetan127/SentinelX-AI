from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.detection import Detection
from app.repositories.base import BaseRepository


class DetectionRepository(BaseRepository[Detection]):
    def __init__(self, session: Session):
        super().__init__(session, Detection)

    def get_by_attack(self, attack_id: UUID) -> List[Detection]:
        statement = select(Detection).where(Detection.attack_id == attack_id)
        return self.session.scalars(statement).all()
