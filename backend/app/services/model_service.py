from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.model import Model
from app.models.dataset import Dataset
from app.models.enums import ModelStatus
from app.repositories.model_repository import ModelRepository
from app.repositories.dataset_repository import DatasetRepository


class ModelService:
    def __init__(self, db: Session):
        self.db = db
        self.model_repo = ModelRepository(db)
        self.dataset_repo = DatasetRepository(db)

    def create_model(
        self,
        name: str,
        algorithm: str,
        dataset: str,
        version: str,
        accuracy: float,
        precision: float,
        recall: float,
        f1_score: float,
        file_path: str,
        trained_at,
        is_active: bool = True,
    ) -> Model:
        # Find or create dataset dynamically
        dataset_record = self.dataset_repo.get_by_name(dataset)
        if not dataset_record:
            dataset_record = Dataset(
                name=dataset,
                version="v1.0",
                description=f"Auto-generated dataset from legacy import: {dataset}",
                source="import",
                uploaded_at=datetime.now(timezone.utc),
            )
            self.dataset_repo.add(dataset_record)
            self.db.flush()

        model_status = ModelStatus.PRODUCTION if is_active else ModelStatus.ARCHIVED

        model = Model(
            dataset_id=dataset_record.id,
            algorithm=algorithm,
            version=version,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            model_file=file_path,
            status=model_status,
            created_at=trained_at or datetime.now(timezone.utc),
        )
        try:
            self.model_repo.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model
        except Exception:
            self.db.rollback()
            raise

    def get_model(self, model_id: UUID) -> Model:
        return self.model_repo.get(model_id)

    def list_models(self, limit: int = 100, offset: int = 0) -> List[Model]:
        return self.model_repo.list(limit=limit, offset=offset)

    def average_accuracy(self) -> float:
        return self.model_repo.average_accuracy()
