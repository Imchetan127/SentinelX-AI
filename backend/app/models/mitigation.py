from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Mitigation(Base):
    __tablename__ = "mitigations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_id = Column(UUID(as_uuid=True), ForeignKey("attacks.id", ondelete="CASCADE"), nullable=False, index=True)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("detections.id", ondelete="CASCADE"), nullable=True, index=True)
    recommended_action = Column(String(64), nullable=False)
    action_taken = Column(String(64), nullable=False)
    rule_applied = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    attack = relationship("Attack", back_populates="mitigations")
    detection = relationship("Detection", back_populates="mitigations")
