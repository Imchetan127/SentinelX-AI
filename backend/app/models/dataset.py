import uuid
from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(128), nullable=False)
    version = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(256), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    models = relationship("Model", back_populates="dataset_ref", cascade="all, delete-orphan")
