from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get(self, record_id: UUID) -> Optional[ModelType]:
        return self.session.get(self.model, record_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        statement = select(self.model)
        if hasattr(self.model, "is_deleted"):
            statement = statement.where(self.model.is_deleted == False)
        statement = statement.limit(limit).offset(offset)
        return self.session.scalars(statement).all()

    def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        return instance

    def soft_delete(self, instance: ModelType) -> ModelType:
        if hasattr(instance, "is_deleted"):
            instance.is_deleted = True
            instance.deleted_at = datetime.utcnow()
            self.session.add(instance)
        else:
            self.session.delete(instance)
        return instance

    def count(self) -> int:
        statement = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted"):
            statement = statement.where(self.model.is_deleted == False)
        return int(self.session.scalar(statement) or 0)
