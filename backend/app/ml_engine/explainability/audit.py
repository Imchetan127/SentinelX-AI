"""AuditIntegration — thin wrapper for XAI-specific audit events.

Keeps all three event strings in one place and delegates to the
existing AuditService. Nothing else in the explainability module
imports AuditService directly.
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.audit_service import AuditService

logger = logging.getLogger("Explainability.Audit")

# Canonical XAI audit event names
EVENT_GENERATED  = "EXPLANATION_GENERATED"
EVENT_FAILED     = "EXPLANATION_FAILED"
EVENT_VALIDATED  = "EXPLANATION_VALIDATED"


class AuditIntegration:
    """Emits immutable audit events for the XAI pipeline."""

    def __init__(self, db: Session):
        self._audit = AuditService(db)

    def log_generated(
        self,
        prediction_id: UUID,
        explanation_id: str,
        algorithm: str,
        user_id: Optional[UUID] = None,
    ) -> None:
        try:
            expl_uuid: Optional[UUID] = UUID(explanation_id)
        except (ValueError, AttributeError):
            expl_uuid = None
        self._audit.log_action(
            user_id=user_id,
            action=EVENT_GENERATED,
            resource="Explanation",
            resource_id=expl_uuid,
            ip_address="127.0.0.1",
            status="success",
            details=(
                f"SHAP explanation generated for prediction '{prediction_id}'. "
                f"algorithm={algorithm}, explanation_id={explanation_id}."
            ),
        )

    def log_validated(
        self,
        prediction_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> None:
        self._audit.log_action(
            user_id=user_id,
            action=EVENT_VALIDATED,
            resource="Explanation",
            resource_id=None,
            ip_address="127.0.0.1",
            status="success",
            details=f"Explanation validated for prediction '{prediction_id}'.",
        )

    def log_failed(
        self,
        prediction_id: Optional[UUID],
        reason: str,
        user_id: Optional[UUID] = None,
    ) -> None:
        self._audit.log_action(
            user_id=user_id,
            action=EVENT_FAILED,
            resource="Explanation",
            resource_id=None,
            ip_address="127.0.0.1",
            status="failure",
            details=(
                f"Explanation failed for prediction '{prediction_id}'. "
                f"Reason: {reason}"
            ),
        )
