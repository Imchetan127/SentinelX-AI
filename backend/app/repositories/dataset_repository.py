from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, session: Session):
        super().__init__(session, Dataset)

    def get_by_name(self, name: str) -> Dataset | None:
        statement = select(Dataset).where(Dataset.name == name)
        return self.session.scalars(statement).first()
