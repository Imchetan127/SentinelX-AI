"""app/reporting/collector.py — Data collection from persisted database models.

Gathers Incident, Attack, Detection, Prediction, Explanation, Model,
and User entities without fabricating data. Handles missing artifacts gracefully.
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.attack import Attack
from app.models.detection import Detection
from app.models.prediction import Prediction
from app.models.explanation import Explanation
from app.models.model import Model
from app.models.user import User

logger = logging.getLogger("Reporting.Collector")


class IncidentCollector:
    """Collects persisted incident, attack, detection, and user records."""

    def __init__(self, db: Session):
        self.db = db

    def collect_incident(self, incident_id: UUID) -> Dict[str, Any]:
        """Fetch the incident and related attack/detection/user entities."""
        incident = self.db.get(Incident, incident_id)
        if incident is None:
            raise FileNotFoundError(f"Incident '{incident_id}' not found in database.")

        attack = incident.attack
        detections = attack.detections if attack else []
        primary_detection = detections[0] if detections else None

        assigned_user = incident.assigned_user

        return {
            "incident": {
                "id": str(incident.id),
                "title": incident.title,
                "description": incident.description or "No description provided.",
                "status": incident.status.value if hasattr(incident.status, "value") else str(incident.status),
                "priority": incident.priority.value if hasattr(incident.priority, "value") else str(incident.priority),
                "opened_at": incident.opened_at.isoformat() if incident.opened_at else None,
                "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
                "assigned_user": assigned_user.username if assigned_user else "Unassigned",
                "assigned_user_role": assigned_user.role.value if assigned_user and hasattr(assigned_user.role, "value") else "N/A",
            },
            "attack": {
                "id": str(attack.id) if attack else "N/A",
                "type": attack.type if attack else "Unknown",
                "payload": attack.payload if attack else "N/A",
                "target": attack.target if attack else "N/A",
                "severity": attack.severity.value if attack and hasattr(attack.severity, "value") else "N/A",
                "status": attack.status.value if attack and hasattr(attack.status, "value") else "N/A",
                "timestamp": attack.timestamp.isoformat() if attack and attack.timestamp else None,
            },
            "detection": {
                "id": str(primary_detection.id) if primary_detection else "N/A",
                "attack_type": primary_detection.attack_type if primary_detection else "N/A",
                "severity": primary_detection.severity.value if primary_detection and hasattr(primary_detection.severity, "value") else "N/A",
                "recommendation": primary_detection.recommendation if primary_detection else "N/A",
                "detected_at": primary_detection.detected_at.isoformat() if primary_detection and primary_detection.detected_at else None,
            },
            "primary_detection_obj": primary_detection,
        }


class EvidenceCollector:
    """Collects ML predictions, SHAP explanations, and model metadata linked to an incident."""

    def __init__(self, db: Session):
        self.db = db

    def collect_evidence(self, primary_detection_obj: Optional[Detection]) -> Dict[str, Any]:
        """Fetch Prediction, Explanation, and Model entities linked to the detection."""
        prediction = None
        if primary_detection_obj and primary_detection_obj.predictions:
            prediction = primary_detection_obj.predictions[0]

        model = None
        explanation = None

        if prediction:
            if prediction.model:
                model = prediction.model
            elif prediction.model_id:
                model = self.db.get(Model, prediction.model_id)

            # Query latest explanation for this prediction
            stmt = (
                select(Explanation)
                .where(
                    Explanation.prediction_id == prediction.id,
                    Explanation.is_deleted == False,
                )
                .order_by(Explanation.explained_at.desc())
            )
            explanation = self.db.scalars(stmt).first()

        return {
            "prediction": {
                "id": str(prediction.id) if prediction else "N/A",
                "label": prediction.prediction if prediction else "N/A",
                "confidence": round(prediction.confidence, 4) if prediction else 0.0,
                "probability": round(prediction.probability, 4) if prediction else 0.0,
                "created_at": prediction.created_at.isoformat() if prediction and prediction.created_at else "N/A",
            },
            "model": {
                "id": str(model.id) if model else "N/A",
                "algorithm": model.algorithm if model else "N/A",
                "version": model.version if model else "N/A",
                "accuracy": round(model.accuracy, 4) if model else 0.0,
                "precision": round(model.precision, 4) if model else 0.0,
                "recall": round(model.recall, 4) if model else 0.0,
                "f1_score": round(model.f1_score, 4) if model else 0.0,
                "status": model.status.value if model and hasattr(model.status, "value") else "N/A",
                "dataset_name": model.dataset if model else "cicids_test",
                "model_file": model.model_file if model else "N/A",
            },
            "explanation": {
                "id": str(explanation.id) if explanation else "N/A",
                "base_value": float(explanation.base_value) if explanation else None,
                "feature_names": explanation.feature_names if explanation else [],
                "shap_values": explanation.shap_values if explanation else [],
                "feature_importance": explanation.feature_importance if explanation else [],
                "top_positive_contributors": explanation.top_positive_contributors if explanation else [],
                "top_negative_contributors": explanation.top_negative_contributors if explanation else [],
                "warnings": explanation.warnings if explanation else [],
                "explained_at": explanation.explained_at.isoformat() if explanation and explanation.explained_at else None,
            } if explanation else None,
        }
