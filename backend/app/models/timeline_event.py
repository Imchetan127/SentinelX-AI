from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_id = Column(UUID(as_uuid=True), ForeignKey("attacks.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(64), nullable=False)
    title = Column(String(256), nullable=False)
    details = Column(Text, nullable=True)
    severity = Column(String(32), nullable=False, default="INFO")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    attack = relationship("Attack", back_populates="timeline_events")
