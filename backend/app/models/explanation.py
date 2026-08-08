import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Explanation(Base):
    """Persists a SHAP explanation for a single prediction.

    Append-only — explanations are never updated after creation.
    One prediction may have multiple explanation rows (if re-explained),
    but ``ExplanationRepository.get_latest_for_prediction`` returns the most recent.
    """
    __tablename__ = "explanations"

    id = Column(
        PG_UUID(as_uuid=True), primary_key=True,
        default=uuid.uuid4, nullable=False
    )
    # FK to the originating prediction
    prediction_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    # FK to the model that made the prediction
    model_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("models.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Model provenance
    model_version = Column(String(64), nullable=True)
    algorithm     = Column(String(128), nullable=True)

    # SHAP outputs
    base_value = Column(Float, nullable=False)          # SHAP expected value
    feature_names          = Column(JSON, nullable=False)  # ordered list[str]
    shap_values            = Column(JSON, nullable=False)  # ordered list[float]
    feature_importance     = Column(JSON, nullable=False)  # sorted [{feature, shap_value, direction}]
    top_positive_contributors = Column(JSON, nullable=False)  # [{feature, shap_value}]
    top_negative_contributors = Column(JSON, nullable=False)  # [{feature, shap_value}]

    # Prediction context (denormalised for fast retrieval)
    prediction_label = Column(String(64), nullable=True)
    confidence       = Column(Float, nullable=True)

    # Non-fatal warnings accumulated during explanation
    warnings = Column(JSON, nullable=False, default=list)

    explained_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_deleted = Column(Boolean, nullable=False, default=False)

    prediction = relationship("Prediction", foreign_keys=[prediction_id])
    model      = relationship("Model",      foreign_keys=[model_id])
