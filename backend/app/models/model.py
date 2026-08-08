from sqlalchemy import Column, Float, ForeignKey, Integer, String, JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import ModelStatus


class Model(Base, TimestampMixin):
    __tablename__ = "models"

    dataset_id = Column(PG_UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="RESTRICT"), nullable=False)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    algorithm = Column(String(128), nullable=False)
    version = Column(String(64), nullable=False)
    accuracy = Column(Float, nullable=False, default=0.0)
    precision = Column(Float, nullable=False, default=0.0)
    recall = Column(Float, nullable=False, default=0.0)
    f1_score = Column(Float, nullable=False, default=0.0)
    training_duration = Column(Float, nullable=True)
    feature_count = Column(Integer, nullable=True)
    hyperparameters = Column(JSON, nullable=True)
    model_file = Column(String(512), nullable=False)
    status = Column(SQLEnum(ModelStatus, native_enum=True), nullable=False, default=ModelStatus.TRAINING)

    dataset_ref = relationship("Dataset", back_populates="models")
    creator = relationship("User", back_populates="models_created")
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")

    @property
    def name(self):
        return self.algorithm

    @property
    def dataset(self) -> str:
        return self.dataset_ref.name if self.dataset_ref else "unknown"

    @property
    def file_path(self):
        return self.model_file

    @property
    def is_active(self):
        return self.status == ModelStatus.PRODUCTION

    @property
    def trained_at(self):
        return self.created_at
