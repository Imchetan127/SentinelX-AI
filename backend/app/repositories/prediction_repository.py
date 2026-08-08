from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self, session: Session):
        super().__init__(session, Prediction)

    def get_by_detection(self, detection_id: UUID) -> List[Prediction]:
        statement = select(Prediction).where(Prediction.detection_id == detection_id)
        return self.session.scalars(statement).all()

    def get_by_model(self, model_id: UUID) -> List[Prediction]:
        statement = select(Prediction).where(Prediction.model_id == model_id)
        return self.session.scalars(statement).all()
