import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.enums import AttackStatus, Severity


class Attack(Base):
    __tablename__ = "attacks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    type = Column(String(128), nullable=False, index=True)
    payload = Column(Text, nullable=False)
    severity = Column(SQLEnum(Severity, native_enum=True), nullable=False, index=True)
    status = Column(SQLEnum(AttackStatus, native_enum=True), nullable=False, default=AttackStatus.PENDING)
    source_ip = Column(String(45), nullable=True)
    target = Column(String(256), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    creator = relationship("User", back_populates="attacks")
    detections = relationship("Detection", back_populates="attack", cascade="all, delete-orphan")
    incident = relationship("Incident", uselist=False, back_populates="attack")

    @property
    def attack_type(self) -> str:
        return self.type

    @property
    def user_id(self) -> str | None:
        return str(self.created_by) if self.created_by else None

    @property
    def created_at(self) -> str:
        return self.timestamp.isoformat() if self.timestamp else None
