from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.model import Model
from app.models.enums import ModelStatus
from app.repositories.base import BaseRepository


class ModelRepository(BaseRepository[Model]):
    def __init__(self, session: Session):
        super().__init__(session, Model)

    def get_active_models(self, limit: int = 100, offset: int = 0) -> List[Model]:
        statement = select(Model).where(
            Model.status.in_([ModelStatus.PRODUCTION, ModelStatus.STAGING]), 
            Model.is_deleted == False
        ).limit(limit).offset(offset)
        return self.session.scalars(statement).all()

    def average_accuracy(self) -> float:
        statement = select(func.avg(Model.accuracy)).where(
            Model.status.in_([ModelStatus.PRODUCTION, ModelStatus.STAGING, ModelStatus.VALIDATED]), 
            Model.is_deleted == False
        )
        return float(self.session.scalar(statement) or 0.0)

    def get_by_name_and_version(self, name: str, version: str) -> Model | None:
        statement = select(Model).where(Model.algorithm == name, Model.version == version, Model.is_deleted == False)
        return self.session.scalars(statement).first()
