import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    detection_id = Column(PG_UUID(as_uuid=True), ForeignKey("detections.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction = Column(String(256), nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    probability = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False)

    detection = relationship("Detection", back_populates="predictions")
    model = relationship("Model", back_populates="predictions")
