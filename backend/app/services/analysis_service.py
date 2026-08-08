from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.detection import Detection
from app.models.prediction import Prediction
from app.models.enums import Severity
from app.repositories.detection_repository import DetectionRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.attack_repository import AttackRepository


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.detection_repo = DetectionRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.attack_repo = AttackRepository(db)

    def create_analysis(
        self,
        attack_id: UUID,
        model_id: UUID,
        prediction: str,
        confidence: float,
        severity: str,
        recommendation: str | None = None,
        processing_time_ms: int | None = None,
    ):
        try:
            sev_enum = Severity[severity.upper()]
        except KeyError:
            sev_enum = Severity.MEDIUM

        attack = self.attack_repo.get(attack_id)
        attack_type = attack.type if attack else "Unknown"

        detection = Detection(
            attack_id=attack_id,
            severity=sev_enum,
            attack_type=attack_type,
            recommendation=recommendation,
            detected_at=datetime.now(timezone.utc),
        )
        try:
            self.detection_repo.add(detection)
            self.db.flush()

            pred = Prediction(
                detection_id=detection.id,
                model_id=model_id,
                prediction=prediction,
                confidence=confidence,
                probability=confidence,
                created_at=datetime.now(timezone.utc),
            )
            self.prediction_repo.add(pred)
            self.db.commit()
            self.db.refresh(pred)
            self.db.refresh(detection)

            return {
                "id": pred.id,
                "attack_id": detection.attack_id,
                "model_id": pred.model_id,
                "prediction": pred.prediction,
                "confidence": pred.confidence,
                "severity": detection.severity.value,
                "recommendation": detection.recommendation,
                "processing_time_ms": processing_time_ms or 0,
                "created_at": pred.created_at.isoformat(),
            }
        except Exception:
            self.db.rollback()
            raise

    def list_analysis(self, limit: int = 100, offset: int = 0) -> List[dict]:
        predictions = self.prediction_repo.list(limit=limit, offset=offset)
        results = []
        for p in predictions:
            results.append({
                "id": p.id,
                "attack_id": p.detection.attack_id if p.detection else None,
                "model_id": p.model_id,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "severity": p.detection.severity.value if p.detection else "MEDIUM",
                "recommendation": p.detection.recommendation if p.detection else None,
                "processing_time_ms": 0,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            })
        return results

    def get_analysis(self, analysis_id: UUID) -> dict | None:
        p = self.prediction_repo.get(analysis_id)
        if not p:
            return None
        return {
            "id": p.id,
            "attack_id": p.detection.attack_id if p.detection else None,
            "model_id": p.model_id,
            "prediction": p.prediction,
            "confidence": p.confidence,
            "severity": p.detection.severity.value if p.detection else "MEDIUM",
            "recommendation": p.detection.recommendation if p.detection else None,
            "processing_time_ms": 0,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }

    def list_by_attack(self, attack_id: UUID) -> List[dict]:
        statement = select(Prediction).join(Detection).where(Detection.attack_id == attack_id)
        predictions = self.db.scalars(statement).all()
        results = []
        for p in predictions:
            results.append({
                "id": p.id,
                "attack_id": p.detection.attack_id,
                "model_id": p.model_id,
                "prediction": p.prediction,
                "confidence": p.confidence,
                "severity": p.detection.severity.value,
                "recommendation": p.detection.recommendation,
                "processing_time_ms": 0,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            })
        return results

    def record_blue_team_inspection(
        self,
        user_id: UUID | None,
        artifact_type: str,
        threat_detected: bool,
        threat_category: str,
        risk_level: str,
        confidence: float,
        recommendations: List[str],
        payload: str,
        source_ip: str | None = None,
    ) -> dict:
        from app.models.attack import Attack
        from app.models.detection import Detection
        from app.models.prediction import Prediction
        from app.models.incident import Incident
        from app.models.model import Model
        from app.models.enums import Severity, AttackStatus, IncidentStatus, ModelStatus
        from app.services.audit_service import AuditService

        audit_service = AuditService(self.db)
        ip = source_ip or "127.0.0.1"

        try:
            sev_enum = Severity[risk_level.upper()]
        except KeyError:
            sev_enum = Severity.MEDIUM

        attack = Attack(
            created_by=user_id,
            type=threat_category,
            payload=payload,
            target="system",
            severity=sev_enum,
            status=AttackStatus.COMPLETED,
            source_ip=ip,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(attack)
        self.db.flush()

        audit_service.log_action(
            user_id=user_id,
            action="LAUNCH_ATTACK",
            resource="Attack",
            resource_id=attack.id,
            ip_address=ip,
            status="success",
            details=f"Attack simulation recorded: {attack.type} [Severity: {attack.severity.value}]",
        )

        rec_text = "\n".join(recommendations) if recommendations else "No specific recommendation."
        detection = Detection(
            attack_id=attack.id,
            severity=sev_enum,
            attack_type=threat_category,
            recommendation=rec_text,
            detected_at=datetime.now(timezone.utc),
        )
        self.db.add(detection)
        self.db.flush()

        audit_service.log_action(
            user_id=user_id,
            action="ANALYZE_THREAT",
            resource="Detection",
            resource_id=detection.id,
            ip_address=ip,
            status="success",
            details=f"Blue Team threat analyzed: {detection.attack_type} [Severity: {detection.severity.value}]",
        )

        model = self.db.scalars(
            select(Model).where(Model.status == ModelStatus.PRODUCTION, Model.is_deleted == False)
        ).first()
        if not model:
            model = self.db.scalars(select(Model)).first()
        if not model:
            from app.models.dataset import Dataset
            dataset = self.db.scalars(select(Dataset)).first()
            if not dataset:
                dataset = Dataset(name="default_dataset", version="1.0")
                self.db.add(dataset)
                self.db.flush()
            model = Model(
                dataset_id=dataset.id,
                algorithm="xgboost",
                version="v1.0",
                accuracy=0.98,
                model_file="default.bin",
                status=ModelStatus.PRODUCTION,
            )
            self.db.add(model)
            self.db.flush()

        pred = Prediction(
            detection_id=detection.id,
            model_id=model.id,
            prediction="malicious" if threat_detected else "clean",
            confidence=confidence,
            probability=confidence,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(pred)
        self.db.flush()

        audit_service.log_action(
            user_id=user_id,
            action="MODEL_INFERENCE",
            resource="Prediction",
            resource_id=pred.id,
            ip_address=ip,
            status="success",
            details=f"Model {model.algorithm} inference completed with confidence {pred.confidence}",
        )

        incident_created = False
        if threat_detected and sev_enum in [Severity.HIGH, Severity.CRITICAL]:
            existing = self.db.scalars(select(Incident).where(Incident.attack_id == attack.id)).first()
            if not existing:
                incident = Incident(
                    attack_id=attack.id,
                    assigned_to=user_id,
                    title=f"Automated Threat Incident: {detection.attack_type}",
                    description=f"Automated security incident raised for threat type '{detection.attack_type}' with severity {detection.severity.value}.\nMitigation recommendations:\n{detection.recommendation}",
                    priority=sev_enum,
                    status=IncidentStatus.OPEN,
                    created_at=datetime.now(timezone.utc),
                )
                self.db.add(incident)
                self.db.flush()
                incident_created = True

                audit_service.log_action(
                    user_id=user_id,
                    action="CREATE_INCIDENT",
                    resource="Incident",
                    resource_id=incident.id,
                    ip_address=ip,
                    status="success",
                    details=f"Incident automatically created for attack {attack.id} [Severity: {incident.priority.value}]",
                )

        self.db.commit()
        return {
            "attack_id": attack.id,
            "detection_id": detection.id,
            "prediction_id": pred.id,
            "incident_created": incident_created,
        }

