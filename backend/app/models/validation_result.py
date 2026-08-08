import uuid
from sqlalchemy import Column, DateTime, JSON, String, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class ValidationResult(Base):
    """Persists a single validation run for one model version.

    Immutable after creation — validation history is append-only.
    """
    __tablename__ = "validation_results"

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4, nullable=False
    )
    model_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("models.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    validator_version = Column(String(32), nullable=False, default="1.0.0")
    dataset_version   = Column(String(64), nullable=True)
    pipeline_version  = Column(String(64), nullable=True)

    # Full 18-metric evaluation on the hold-out test split
    metrics           = Column(JSON, nullable=True)

    # Stratified k-fold cross-validation (mean / std / CI per metric)
    cv_metrics        = Column(JSON, nullable=True)

    # Per-threshold pass/fail evaluation
    threshold_results = Column(JSON, nullable=True)

    # "PASSED" or "FAILED"
    quality_gate_result  = Column(String(16), nullable=False, default="FAILED")

    # List of failure reason strings (empty list when PASSED)
    quality_gate_reasons = Column(JSON, nullable=False, default=list)

    # Full structured validation report (ValidationReporter output)
    report   = Column(JSON, nullable=True)

    # Non-fatal warning strings accumulated during validation
    warnings = Column(JSON, nullable=False, default=list)

    # When this validation run was executed
    validated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), nullable=False
    )
    is_deleted = Column(Boolean, nullable=False, default=False)

    model = relationship("Model", foreign_keys=[model_id])
