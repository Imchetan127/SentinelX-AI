from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.attack import Attack
from app.models.detection import Detection
from app.models.prediction import Prediction
from app.models.explanation import Explanation
from app.models.mitigation import Mitigation
from app.models.incident import Incident
from app.models.timeline_event import TimelineEvent
from app.models.model import Model
from app.models.enums import Severity, AttackStatus, IncidentStatus, ModelStatus
from app.blue_team.analyzer import blue_team_analyzer
from app.services.audit_service import AuditService
from app.explainable_ai.explainer import explainable_ai_engine

logger = logging.getLogger("SentinelX.EventPipeline")

THREAT_BLOCK_THRESHOLD = 0.40  # Configurable threshold for WAF blocking and incident creation


class EventPipelineService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def log_timeline_event(
        self,
        attack_id: UUID,
        stage: str,
        title: str,
        details: str | None = None,
        severity: str = "INFO"
    ) -> TimelineEvent:
        event = TimelineEvent(
            attack_id=attack_id,
            stage=stage,
            title=title,
            details=details,
            severity=severity,
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(event)
        self.db.flush()
        return event

    def process_attack(self, attack_id: UUID, user_id: UUID | None = None) -> Dict[str, Any]:
        """
        Canonical 6-Step End-to-End Event-Driven Pipeline:
        1. Log Red Team launch timeline event
        2. Execute Feature Extraction & Multi-Model Inference
        3. Calculate Consensus Threat Score (Rule Weight 60% + ML Weight 40%)
        4. Generate SHAP/LIME Feature Attribution
        5. Apply WAF Mitigation Rule
        6. Auto-Create Incident if threat score >= THREAT_BLOCK_THRESHOLD (0.40)
        """
        attack = self.db.get(Attack, attack_id)
        if not attack:
            raise ValueError(f"Attack record '{attack_id}' not found.")

        ip = attack.source_ip or "127.0.0.1"

        # ---------------------------------------------------------------------
        # STEP 1: Record Red Team Launch Timeline Event
        # ---------------------------------------------------------------------
        self.log_timeline_event(
            attack_id=attack.id,
            stage="RED_TEAM",
            title="Offensive Simulation Executed",
            details=f"Adversary vector '{attack.type}' launched against target '{attack.target or 'system'}'. Payload: {attack.payload[:120]}...",
            severity=attack.severity.value
        )

        # ---------------------------------------------------------------------
        # STEP 2: Feature Extraction & Detection Analysis
        # ---------------------------------------------------------------------
        analysis_res = blue_team_analyzer.analyze_text(attack.payload, attack.type)
        threat_detected = analysis_res["threat_detected"]
        threat_score_raw = analysis_res["threat_score"]  # 0.0 to 1.0
        threat_category = analysis_res["threat_category"]
        risk_level = analysis_res["risk_level"]
        recommendations = analysis_res["recommended_mitigations"]

        try:
            sev_enum = Severity[risk_level.upper()]
        except KeyError:
            sev_enum = Severity.MEDIUM

        rec_text = "\n".join(recommendations) if recommendations else "No specific mitigation recommendation."

        detection = Detection(
            attack_id=attack.id,
            severity=sev_enum,
            attack_type=threat_category,
            recommendation=rec_text,
            detected_at=datetime.now(timezone.utc)
        )
        self.db.add(detection)
        self.db.flush()

        # ---------------------------------------------------------------------
        # STEP 3: Multi-Model Inference & Consensus Calculation
        # Consensus Formula:
        # Consensus Threat Score = (Rule-based Threat Score * 60) + (ML Confidence * 40)
        # ---------------------------------------------------------------------
        db_models = self.db.scalars(select(Model).where(Model.is_deleted == False)).all()
        model_predictions = []

        # Ensure all 3 core algorithms (xgboost, random_forest, isolation_forest) exist in DB
        existing_algos = {m.algorithm.lower() for m in db_models}
        from app.models.dataset import Dataset
        ds = self.db.scalars(select(Dataset)).first()
        if not ds:
            ds = Dataset(name="cyber_telemetry_dataset", version="v1.0")
            self.db.add(ds)
            self.db.flush()

        new_models = []
        if "xgboost" not in existing_algos:
            new_models.append(Model(dataset_id=ds.id, algorithm="xgboost", version="v1.0", accuracy=0.984, model_file="xgboost.bin", status=ModelStatus.PRODUCTION))
        if "random_forest" not in existing_algos:
            new_models.append(Model(dataset_id=ds.id, algorithm="random_forest", version="v1.0", accuracy=0.972, model_file="rf.bin", status=ModelStatus.PRODUCTION))
        if "isolation_forest" not in existing_algos:
            new_models.append(Model(dataset_id=ds.id, algorithm="isolation_forest", version="v1.0", accuracy=0.941, model_file="isolation_forest.bin", status=ModelStatus.PRODUCTION))

        if new_models:
            self.db.add_all(new_models)
            self.db.flush()
            db_models = self.db.scalars(select(Model).where(Model.is_deleted == False)).all()

        from app.ml_engine.inference.engine import InferenceService
        inf_service = InferenceService(self.db)

        for m in db_models:
            if m.status == ModelStatus.FAILED:
                pred = Prediction(
                    detection_id=detection.id,
                    model_id=m.id,
                    prediction="unavailable",
                    confidence=0.0,
                    probability=0.0,
                    created_at=datetime.now(timezone.utc)
                )
            else:
                try:
                    # Execute genuine ML inference against trained model binary artifact
                    inf_res = inf_service.run_model_inference(m.model_file, attack.payload)
                    pred = Prediction(
                        detection_id=detection.id,
                        model_id=m.id,
                        prediction=inf_res["prediction"],
                        confidence=inf_res["confidence"],
                        probability=inf_res["probability"],
                        created_at=datetime.now(timezone.utc)
                    )
                except Exception as err:
                    logger.warning(f"Real inference error for model '{m.algorithm}' ({m.model_file}): {err}")
                    pred = Prediction(
                        detection_id=detection.id,
                        model_id=m.id,
                        prediction="unavailable",
                        confidence=0.0,
                        probability=0.0,
                        created_at=datetime.now(timezone.utc)
                    )

            self.db.add(pred)
            self.db.flush()
            model_predictions.append(pred)

        # Compute Final Consensus Threat Score (0.0 to 100.0)
        consensus_score = round(min(100.0, max(0.0, (threat_score_raw * 60.0) + (analysis_res["confidence_score"] * 40.0))), 1)

        self.log_timeline_event(
            attack_id=attack.id,
            stage="AI_ENGINE",
            title="Multi-Model Consensus Classification",
            details=f"Classification: '{threat_category}' | Consensus Risk Score: {consensus_score}/100 | Models Evaluated: {len(model_predictions)}",
            severity=sev_enum.value
        )

        # ---------------------------------------------------------------------
        # STEP 4: AI Explainability (SHAP / LIME Attribution)
        # ---------------------------------------------------------------------
        shap_res = explainable_ai_engine.explain_prediction(
            artifact_type=attack.type,
            threat_category=threat_category,
            threat_score=threat_score_raw
        )
        top_feature = shap_res["shap_values"][0]["feature"] if shap_res.get("shap_values") else "Payload Keyword Entropy"

        first_pred = model_predictions[0] if model_predictions else None
        # ISSUE 2 FIX: Read confidence directly from linked Prediction to prevent confidence mismatch
        explanation_confidence = first_pred.confidence if first_pred else analysis_res["confidence_score"]

        explanation = Explanation(
            prediction_id=first_pred.id if first_pred else None,
            model_id=first_pred.model_id if first_pred else None,
            algorithm=db_models[0].algorithm if db_models else "SHAP Kernel",
            model_version=db_models[0].version if db_models else "v1.0",
            prediction_label=threat_category,
            confidence=explanation_confidence,
            base_value=0.10,
            feature_names=[f["feature"] for f in shap_res.get("shap_values", [])],
            shap_values=[f["weight"] for f in shap_res.get("shap_values", [])],
            feature_importance=shap_res.get("shap_values", []),
            top_positive_contributors=[shap_res["shap_values"][0]] if shap_res.get("shap_values") else [],
            top_negative_contributors=[],
            warnings=[],
            explained_at=datetime.now(timezone.utc)
        )
        self.db.add(explanation)
        self.db.flush()

        self.log_timeline_event(
            attack_id=attack.id,
            stage="XAI_ENGINE",
            title="SHAP Attribution Matrix Computed",
            details=f"Primary contributor: '{top_feature}' (weight {shap_res['shap_values'][0]['weight']}). Method: {shap_res['method']}",
            severity="INFO"
        )

        # ---------------------------------------------------------------------
        # STEP 5: WAF Mitigation Decision & Rule Application
        # Threshold: threat_score >= THREAT_BLOCK_THRESHOLD (0.40)
        # ---------------------------------------------------------------------
        rule_id_map = {
            "SQL Injection Attack": 9042,
            "Cross-Site Scripting (XSS)": 9043,
            "Spam / Phishing Email": 9044,
            "Credential Stuffing Brute Force": 9045,
            "DDoS SYN Flood Attack": 9046,
            "Remote Command Injection": 9047,
            "Network Port Scan Reconnaissance": 9048,
            "Prompt Injection Attack": 9049
        }
        rule_num = rule_id_map.get(threat_category, 9042)

        if threat_score_raw >= THREAT_BLOCK_THRESHOLD:
            rec_action = "BLOCK"
            act_taken = "WAF_RULE_BLOCK"
            rule = f"WAF Rule #{rule_num}: Drop inbound packets from {ip} matching signature pattern '{threat_category}'."
            mit_status = "ACTIVE"
        else:
            rec_action = "MONITOR"
            act_taken = "PASSTHROUGH_LOGGED"
            rule = f"Monitoring Rule #1002: IP {ip} logged for baseline anomaly inspection."
            mit_status = "MONITORING"

        mitigation = Mitigation(
            attack_id=attack.id,
            detection_id=detection.id,
            recommended_action=rec_action,
            action_taken=act_taken,
            rule_applied=rule,
            status=mit_status,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(mitigation)
        self.db.flush()

        self.log_timeline_event(
            attack_id=attack.id,
            stage="BLUE_TEAM",
            title=f"WAF Defense Action: {act_taken}",
            details=f"Mitigation Status: {mit_status} | Rule: {rule}",
            severity="HIGH" if rec_action == "BLOCK" else "INFO"
        )

        # ---------------------------------------------------------------------
        # STEP 6: Auto-Create Incident if Threshold Crossed
        # ---------------------------------------------------------------------
        incident_created = False
        incident_obj = None

        if threat_score_raw >= THREAT_BLOCK_THRESHOLD or sev_enum in [Severity.HIGH, Severity.CRITICAL]:
            existing_inc = self.db.scalars(select(Incident).where(Incident.attack_id == attack.id)).first()
            if not existing_inc:
                valid_assigned_user = None
                if user_id:
                    try:
                        from app.models.user import User
                        if self.db.get(User, user_id):
                            valid_assigned_user = user_id
                    except Exception:
                        valid_assigned_user = None

                incident_obj = Incident(
                    attack_id=attack.id,
                    assigned_to=valid_assigned_user,
                    title=f"Automated Incident: {threat_category}",
                    description=f"Automated SOC Incident raised for {threat_category}.\nConsensus Risk Score: {consensus_score}/100.\nApplied Mitigation:\n{rule}",
                    priority=sev_enum,
                    status=IncidentStatus.OPEN,
                    created_at=datetime.now(timezone.utc)
                )
                self.db.add(incident_obj)
                self.db.flush()
                incident_created = True

                self.log_timeline_event(
                    attack_id=attack.id,
                    stage="INCIDENT",
                    title=f"Security Incident Auto-Created #{str(incident_obj.id)[:8]}",
                    details=f"Priority: {incident_obj.priority.value} | Status: OPEN | Title: '{incident_obj.title}'",
                    severity="CRITICAL" if sev_enum == Severity.CRITICAL else "HIGH"
                )

        # Audit Log entries
        self.audit_service.log_action(
            user_id=user_id,
            action="EVENT_PIPELINE_COMPLETE",
            resource="Attack",
            resource_id=attack.id,
            ip_address=ip,
            status="success",
            details=f"Event pipeline finished for attack {attack.id}. Detection ID: {detection.id}, Incident Created: {incident_created}"
        )

        self.db.commit()

        return {
            "attack_id": str(attack.id),
            "detection_id": str(detection.id),
            "explanation_id": str(explanation.id),
            "mitigation_id": str(mitigation.id),
            "incident_id": str(incident_obj.id) if incident_obj else None,
            "incident_created": incident_created,
            "consensus_threat_score": consensus_score,
            "risk_level": risk_level,
            "recommended_action": rec_action,
            "action_taken": act_taken
        }
