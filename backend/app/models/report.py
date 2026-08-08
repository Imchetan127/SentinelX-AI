from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    incident_id = Column(PG_UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="RESTRICT"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    pdf_path = Column(String(512), nullable=True)
    sha256_hash = Column(String(64), nullable=True)
    title = Column(String(256), nullable=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    incident = relationship("Incident", back_populates="reports")
    creator = relationship("User", back_populates="reports_generated")

    @property
    def report_type(self):
        return self.summary or "Enterprise Incident Report"

    @property
    def file_path(self):
        return self.pdf_path or self.recommendations or ""

    @property
    def generated_by(self):
        return self.created_by

