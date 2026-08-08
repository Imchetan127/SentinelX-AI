"""app/reporting/service.py — Incident Reporting Engine Orchestrator.

Coordinates IncidentCollector → EvidenceCollector → TimelineBuilder →
ThreatIntel & MITRE → AI & SHAP formatters → RecommendationEngine →
PDFRenderer → SHA256 Hashing → ReportPersistence → ReportAuditIntegration.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.report import Report
from app.reporting.collector import IncidentCollector, EvidenceCollector
from app.reporting.timeline import TimelineBuilder
from app.reporting.mitre import ThreatIntelligenceFormatter
from app.reporting.formatters import AIAnalysisFormatter, SHAPFormatter, RecommendationEngine
from app.reporting.renderer import PDFRenderer
from app.reporting.integrity import ReportIntegrityVerifier
from app.reporting.persistence import ReportPersistence
from app.reporting.audit import ReportAuditIntegration

logger = logging.getLogger("Reporting.Service")


class ReportService:
    """Orchestrates end-to-end PDF incident report generation, persistence, and audit logging."""

    def __init__(
        self,
        db: Session,
        reports_dir: Optional[str] = None,
    ):
        self.db = db
        # Centralized report storage directory
        self.reports_dir = reports_dir or getattr(settings, "REPORTS_DIR", "../reports")
        os.makedirs(self.reports_dir, exist_ok=True)

        # Sub-components
        self.incident_collector = IncidentCollector(db)
        self.evidence_collector = EvidenceCollector(db)
        self.timeline_builder = TimelineBuilder(db)
        self.threat_intel_formatter = ThreatIntelligenceFormatter()
        self.ai_formatter = AIAnalysisFormatter()
        self.shap_formatter = SHAPFormatter()
        self.rec_engine = RecommendationEngine()
        self.pdf_renderer = PDFRenderer(output_dir=self.reports_dir)
        self.integrity_verifier = ReportIntegrityVerifier()
        self.persistence = ReportPersistence(db)
        self.audit = ReportAuditIntegration(db)

    def generate_report(
        self,
        incident_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> Report:
        """Generate, render, hash, persist, and audit a PDF report for *incident_id*."""
        try:
            # 1. Collect Incident & Attack entities
            inc_data = self.incident_collector.collect_incident(incident_id)

            # 2. Collect ML Evidence & SHAP Explanation
            evidence_data = self.evidence_collector.collect_evidence(
                inc_data.get("primary_detection_obj")
            )

            # 3. Build Timeline
            timeline_data = self.timeline_builder.build_timeline(
                incident_id=str(incident_id),
                attack_id=inc_data["attack"]["id"],
                prediction_id=evidence_data["prediction"]["id"],
                explanation_id=evidence_data["explanation"]["id"] if evidence_data.get("explanation") else None,
            )

            # 4. Format Threat Intel & MITRE ATT&CK
            threat_intel = self.threat_intel_formatter.format(inc_data["attack"]["type"])

            # 5. Format AI Analysis
            ai_analysis = self.ai_formatter.format(evidence_data)

            # 6. Format SHAP Explanation
            shap_analysis = self.shap_formatter.format(evidence_data.get("explanation"))

            # 7. Generate Deterministic Recommendations
            recs = self.rec_engine.generate_recommendations(inc_data["attack"]["type"])

            # 8. Assemble canonical report document
            generated_at_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            report_id_temp = f"REP-{str(incident_id)[:8].upper()}"

            report_data: Dict[str, Any] = {
                "report_id": report_id_temp,
                "incident_id": str(incident_id),
                "generated_at": generated_at_str,
                "incident": inc_data["incident"],
                "attack": inc_data["attack"],
                "detection": inc_data["detection"],
                "evidence": evidence_data,
                "ai_analysis": ai_analysis,
                "shap": shap_analysis,
                "timeline": timeline_data,
                "threat_intel": threat_intel,
                "recommendations": recs,
            }

            # 9. Render PDF file
            pdf_filename = f"report_incident_{incident_id}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
            pdf_path = self.pdf_renderer.render(report_data, pdf_filename)

            # 10. Compute SHA256 hash
            sha256_hash = self.integrity_verifier.compute_sha256(pdf_path)

            # 11. Persist Report DB record
            report_title = f"Incident Report: {inc_data['incident']['title']}"
            report_row = self.persistence.save_report(
                incident_id=incident_id,
                pdf_path=pdf_path,
                sha256_hash=sha256_hash,
                title=report_title,
                generated_by=user_id,
                version=1,
                summary=report_title,
                recommendations=pdf_path,
            )

            # 12. Audit event: REPORT_GENERATED
            self.audit.log_generated(
                incident_id=incident_id,
                report_id=report_row.id,
                sha256_hash=sha256_hash,
                user_id=user_id,
            )

            logger.info("ReportService: report '%s' generated for incident '%s'.", report_row.id, incident_id)
            return report_row

        except Exception as exc:
            self.audit.log_failed(incident_id, str(exc), user_id)
            logger.error("ReportService: generation failed for incident '%s': %s", incident_id, exc)
            raise

    def get_report(self, report_id: UUID) -> Optional[Report]:
        """Fetch Report by ID."""
        return self.db.get(Report, report_id)

    def list_reports(self, limit: int = 100, offset: int = 0) -> List[Report]:
        """List generated reports."""
        return self.persistence.repo.list(limit=limit, offset=offset)

    def list_by_incident(self, incident_id: UUID) -> List[Report]:
        """List reports for a specific incident."""
        return self.persistence.repo.get_by_incident(incident_id)

    def download_report(self, report_id: UUID, user_id: Optional[UUID] = None) -> Tuple[str, str]:
        """Verify report exists, log REPORT_DOWNLOADED, and return (pdf_path, filename)."""
        report = self.get_report(report_id)
        if report is None:
            raise FileNotFoundError(f"Report '{report_id}' not found.")

        pdf_path = report.pdf_path or report.recommendations
        if not pdf_path or not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Report PDF file missing from path: {pdf_path}")

        self.audit.log_downloaded(report_id=report_id, user_id=user_id)
        filename = os.path.basename(pdf_path)
        return pdf_path, filename

    def verify_report_integrity(self, report_id: UUID) -> Dict[str, Any]:
        """Recompute SHA256 hash of PDF on disk and verify integrity."""
        return self.integrity_verifier.verify_report(self.db, report_id)
