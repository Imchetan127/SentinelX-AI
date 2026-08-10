import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import Severity


class Detection(Base):
    __tablename__ = "detections"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    attack_id = Column(PG_UUID(as_uuid=True), ForeignKey("attacks.id", ondelete="CASCADE"), nullable=False)
    severity = Column(SQLEnum(Severity, native_enum=True), nullable=False)
    attack_type = Column(String(128), nullable=False)
    recommendation = Column(Text, nullable=True)
    detected_at = Column(DateTime(timezone=True), nullable=False)

    attack = relationship("Attack", back_populates="detections")
    predictions = relationship("Prediction", back_populates="detection", cascade="all, delete-orphan")
    mitigations = relationship("Mitigation", back_populates="detection", cascade="all, delete-orphan")
