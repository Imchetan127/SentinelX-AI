from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import IncidentStatus, Severity


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    attack_id = Column(PG_UUID(as_uuid=True), ForeignKey("attacks.id", ondelete="RESTRICT"), unique=True, nullable=False)
    assigned_to = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(SQLEnum(IncidentStatus, native_enum=True), nullable=False, default=IncidentStatus.OPEN, index=True)
    priority = Column(SQLEnum(Severity, native_enum=True), nullable=False, default=Severity.MEDIUM, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)

    attack = relationship("Attack", back_populates="incident")
    assigned_user = relationship("User", back_populates="incidents_assigned")
    reports = relationship("Report", back_populates="incident", cascade="all, delete-orphan")

    @property
    def analysis_result_id(self):
        if self.attack and self.attack.detections:
            det = self.attack.detections[0]
            if det.predictions:
                return det.predictions[0].id
        return None

    @property
    def assigned_user_id(self):
        return self.assigned_to

    @property
    def opened_at(self):
        return self.created_at

    @property
    def closed_at(self):
        return self.deleted_at
