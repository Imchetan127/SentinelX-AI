from typing import List
import uuid
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    last_login = Column(DateTime(timezone=True), nullable=True)

    attacks = relationship("Attack", back_populates="creator")
    incidents_assigned = relationship("Incident", back_populates="assigned_user")
    audit_logs = relationship("AuditLog", back_populates="user")
    reports_generated = relationship("Report", back_populates="creator")
    models_created = relationship("Model", back_populates="creator")
