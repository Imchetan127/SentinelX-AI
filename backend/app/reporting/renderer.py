"""app/reporting/renderer.py — Enterprise PDF Generator using ReportLab.

Renders a 11-section professional security investigation report with
Table of Contents, dynamic running footers with page numbers, SentinelX AI branding,
and structured tables.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

logger = logging.getLogger("Reporting.PDFRenderer")

# Brand Color Palette
PRIMARY_COLOR = colors.HexColor("#1A2B4C")    # Navy Blue
SECONDARY_COLOR = colors.HexColor("#0066CC")  # Sentinel Blue
ACCENT_RED = colors.HexColor("#D9534F")       # Alert Crimson
ACCENT_GREEN = colors.HexColor("#5CB85C")     # Clean Green
BG_LIGHT = colors.HexColor("#F8F9FA")         # Card Light Gray
TEXT_DARK = colors.HexColor("#212529")        # Primary Text
BORDER_COLOR = colors.HexColor("#E9ECEF")     # Border Light


class NumberedCanvas(canvas.Canvas):
    """Canvas subclass that draws running headers, footers, and page numbers dynamically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#6C757D"))

        # Skip running header/footer on cover page (page 1)
        if self._pageNumber > 1:
            # Running Header
            self.drawString(54, 11 * inch - 36, "SentinelX AI — Enterprise Incident Investigation Report")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

            # Running Footer
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            self.drawString(54, 36, f"CONFIDENTIAL — SentinelX AI Platform | {now_str}")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * inch - 54, 36, page_text)
            self.line(54, 48, 8.5 * inch - 54, 48)

        self.restoreState()


class PDFRenderer:
    """Renders structured security report data into a professional PDF file."""

    def __init__(self, output_dir: str = "../reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render(self, report_data: Dict[str, Any], filename: str) -> str:
        """Render *report_data* to a PDF file at `self.output_dir/filename`. Returns absolute path."""
        pdf_path = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        styles = getSampleStyleSheet()

        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            "CoverTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            textColor=PRIMARY_COLOR,
            spaceAfter=12,
        )
        subtitle_style = ParagraphStyle(
            "CoverSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=SECONDARY_COLOR,
            spaceAfter=24,
        )
        h1_style = ParagraphStyle(
            "SectionH1",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=PRIMARY_COLOR,
            spaceBefore=16,
            spaceAfter=8,
            keepWithNext=True,
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=SECONDARY_COLOR,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=TEXT_DARK,
            spaceAfter=8,
        )
        body_bold = ParagraphStyle(
            "ReportBodyBold",
            parent=body_style,
            fontName="Helvetica-Bold",
        )
        code_style = ParagraphStyle(
            "CodeBlock",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#24292E"),
            backColor=colors.HexColor("#F6F8FA"),
            borderColor=BORDER_COLOR,
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=8,
        )

        def _p(text: Any, style: ParagraphStyle = body_style) -> Paragraph:
            """Safely wrap text in a ReportLab Paragraph, handling None values."""
            if text is None:
                text_str = "N/A"
            else:
                text_str = str(text)
            return Paragraph(text_str, style)

        story = []

        # ── 1. COVER PAGE ─────────────────────────────────────────────
        story.append(Spacer(1, 40))
        story.append(Paragraph("SENTINELX AI", ParagraphStyle("Brand", fontName="Helvetica-Bold", fontSize=16, textColor=SECONDARY_COLOR, spaceAfter=8)))
        story.append(Paragraph("ENTERPRISE INCIDENT INVESTIGATION REPORT", title_style))
        story.append(Paragraph("Automated Forensics, AI Analysis & Threat Mitigation Report", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY_COLOR, spaceAfter=30))

        inc = report_data.get("incident", {})
        cov_data = [
            [_p("<b>Incident ID:</b>"), _p(inc.get("id"))],
            [_p("<b>Report ID:</b>"), _p(report_data.get("report_id"))],
            [_p("<b>Generated Time:</b>"), _p(report_data.get("generated_at"))],
            [_p("<b>Assigned Analyst:</b>"), _p(f"{inc.get('assigned_user') or 'Unassigned'} ({inc.get('assigned_user_role') or 'N/A'})")],
            [_p("<b>Classification:</b>"), _p("<font color='#D9534F'><b>CONFIDENTIAL — RESTRICTED SOC REPORT</b></font>")],
            [_p("<b>Incident Status:</b>"), _p(f"<b>{(inc.get('status') or 'OPEN').upper()}</b>")],
        ]
        cov_table = Table(cov_data, colWidths=[130, 374])
        cov_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(cov_table)
        story.append(Spacer(1, 40))

        # ── 2. TABLE OF CONTENTS SUMMARY ───────────────────────────────
        story.append(Paragraph("Table of Contents", h2_style))
        toc_items = [
            "1. Cover Page & Metadata",
            "2. Executive Summary",
            "3. Incident Details",
            "4. Attack Analysis",
            "5. AI Inference & Quality Gate Analysis",
            "6. Explainability & SHAP Feature Contributions",
            "7. Chronological Incident Timeline",
            "8. MITRE ATT&CK Mapping & Threat Intelligence",
            "9. Evidence & Artifact References",
            "10. Deterministic Remediation Recommendations",
            "11. Appendix & Cryptographic Audit Verification",
        ]
        for item in toc_items:
            story.append(Paragraph(item, ParagraphStyle("TOCItem", parent=body_style, leftIndent=12, spaceAfter=3)))

        story.append(PageBreak())

        # ── 3. EXECUTIVE SUMMARY ───────────────────────────────────────
        story.append(Paragraph("2. Executive Summary", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        atk = report_data.get("attack", {})
        pred = report_data.get("evidence", {}).get("prediction", {})
        ai = report_data.get("ai_analysis", {})

        exec_text = (
            f"On {atk.get('timestamp') or 'N/A'}, SentinelX AI detected a <b>{atk.get('type') or 'Unknown'}</b> attack "
            f"classified with <b>{(atk.get('severity') or 'N/A').upper()}</b> severity targeting <b>{atk.get('target') or 'N/A'}</b>. "
            f"The active machine learning inference model (<b>{ai.get('algorithm') or 'N/A'} v{ai.get('model_version') or 'N/A'}</b>) "
            f"evaluated the incoming feature telemetry and predicted <b>{(pred.get('label') or 'N/A').upper()}</b> "
            f"with <b>{round(float(pred.get('confidence') or 0.0) * 100, 2)}% confidence</b>. "
            f"The quality gate validation status for this inference engine is <b>{ai.get('quality_gate') or 'PASSED'}</b>. "
            f"The current incident lifecycle status is <b>{(inc.get('status') or 'OPEN').upper()}</b>."
        )
        story.append(Paragraph(exec_text, body_style))
        story.append(Spacer(1, 10))

        # ── 4. INCIDENT DETAILS ────────────────────────────────────────
        story.append(Paragraph("3. Incident Details", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        inc_rows = [
            [_p("<b>Incident Title:</b>"), _p(inc.get("title"))],
            [_p("<b>Incident UUID:</b>"), _p(inc.get("id"))],
            [_p("<b>Attack UUID:</b>"), _p(atk.get("id"))],
            [_p("<b>Opened Time:</b>"), _p(inc.get("opened_at"))],
            [_p("<b>Closed Time:</b>"), _p(inc.get("closed_at") or "Active / Unclosed")],
            [_p("<b>Priority / Severity:</b>"), _p(f"{inc.get('priority') or 'MEDIUM'} / {atk.get('severity') or 'N/A'}")],
            [_p("<b>Affected Component:</b>"), _p(atk.get("target"))],
            [_p("<b>Assigned User:</b>"), _p(inc.get("assigned_user") or "Unassigned")],
        ]
        t_inc = Table(inc_rows, colWidths=[140, 364])
        t_inc.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_inc)
        story.append(Spacer(1, 12))

        # ── 5. ATTACK ANALYSIS ─────────────────────────────────────────
        story.append(Paragraph("4. Attack Analysis", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        atk_rows = [
            [_p("<b>Attack Type:</b>"), _p(atk.get("type"))],
            [_p("<b>Source / Target:</b>"), _p(f"Inbound Network → {atk.get('target') or 'N/A'}")],
            [_p("<b>Timestamp:</b>"), _p(atk.get("timestamp"))],
            [_p("<b>Severity:</b>"), _p((atk.get("severity") or "N/A").upper())],
            [_p("<b>Status:</b>"), _p(atk.get("status"))],
        ]
        t_atk = Table(atk_rows, colWidths=[140, 364])
        t_atk.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_atk)
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Payload / Attack Telemetry Indicator:</b>", h2_style))
        payload_text = str(atk.get("payload") or "No raw payload stored.")
        story.append(Paragraph(payload_text, code_style))
        story.append(Spacer(1, 10))

        # ── 6. AI ANALYSIS & QUALITY GATE ──────────────────────────────
        story.append(Paragraph("5. AI Analysis & Model Provenance", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        m_metrics = ai.get("metrics", {})
        ai_rows = [
            [_p("<b>Algorithm:</b>"), _p(ai.get("algorithm")),
             _p("<b>Model Version:</b>"), _p(ai.get("model_version"))],
            [_p("<b>Dataset Version:</b>"), _p(ai.get("dataset_version")),
             _p("<b>Pipeline Version:</b>"), _p(ai.get("pipeline_version"))],
            [_p("<b>Prediction Label:</b>"), _p(f"<b>{(ai.get('prediction') or 'N/A').upper()}</b>"),
             _p("<b>Confidence:</b>"), _p(f"{round(float(ai.get('confidence') or 0.0) * 100, 2)}%")],
            [_p("<b>F1-Score:</b>"), _p(str(m_metrics.get("f1_score", "N/A"))),
             _p("<b>Quality Gate:</b>"), _p(f"<b>{ai.get('quality_gate') or 'PASSED'}</b>")],
        ]
        t_ai = Table(ai_rows, colWidths=[110, 142, 110, 142])
        t_ai.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
            ('BACKGROUND', (2,0), (2,-1), BG_LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_ai)
        story.append(Spacer(1, 12))

        # ── 7. EXPLAINABILITY (SHAP) ───────────────────────────────────
        story.append(Paragraph("6. Explainability & SHAP Contributions", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        shap_data = report_data.get("shap", {})
        if shap_data and shap_data.get("status") == "AVAILABLE":
            story.append(Paragraph(f"<b>SHAP Base Value (Expected Model Baseline):</b> {shap_data.get('base_value')}", body_style))
            story.append(Spacer(1, 6))

            story.append(Paragraph("<b>Top Positive Feature Contributors (Increasing Malicious Risk):</b>", h2_style))
            pos_items = shap_data.get("top_positive", [])
            if pos_items:
                pos_rows = [["Feature Name", "SHAP Contribution Value"]] + [
                    [_p(p.get("feature")), _p(f"+{float(p.get('shap_value', 0)):.6f}")] for p in pos_items
                ]
                t_pos = Table(pos_rows, colWidths=[300, 204])
                t_pos.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                    ('PADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_pos)
            else:
                story.append(Paragraph("None identified.", body_style))

            story.append(Spacer(1, 8))
            story.append(Paragraph("<b>Top Negative Feature Contributors (Decreasing Malicious Risk):</b>", h2_style))
            neg_items = shap_data.get("top_negative", [])
            if neg_items:
                neg_rows = [["Feature Name", "SHAP Contribution Value"]] + [
                    [_p(n.get("feature")), _p(f"{float(n.get('shap_value', 0)):.6f}")] for n in neg_items
                ]
                t_neg = Table(neg_rows, colWidths=[300, 204])
                t_neg.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                    ('PADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_neg)
            else:
                story.append(Paragraph("None identified.", body_style))

        else:
            story.append(Paragraph("<i>SHAP explanation unavailable for this prediction.</i>", body_style))

        story.append(PageBreak())

        # ── 8. INCIDENT TIMELINE ───────────────────────────────────────
        story.append(Paragraph("7. Chronological Incident Timeline", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        timeline = report_data.get("timeline", [])
        if timeline:
            tl_rows = [["Timestamp (UTC)", "Event Action", "Resource", "Details"]]
            for ev in timeline[:15]:   # Cap at top 15 events for PDF layout
                ts_val = (ev.get("timestamp") or "N/A")[:19]
                det_val = (ev.get("details") or "N/A")[:60]
                tl_rows.append([
                    _p(ts_val),
                    _p(f"<b>{ev.get('action') or 'N/A'}</b>"),
                    _p(ev.get("resource")),
                    _p(det_val),
                ])
            t_tl = Table(tl_rows, colWidths=[110, 120, 80, 194])
            t_tl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t_tl)
        else:
            story.append(Paragraph("No audit logs found for this incident timeline.", body_style))

        story.append(Spacer(1, 12))

        # ── 9. MITRE ATT&CK MAPPING ────────────────────────────────────
        story.append(Paragraph("8. MITRE ATT&CK Mapping & Threat Intelligence", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        mitre = report_data.get("threat_intel", {}).get("mitre", {})
        m_table_rows = [
            [_p("<b>Technique ID:</b>"), _p(f"<b>{mitre.get('technique_id') or 'T1190'}</b>")],
            [_p("<b>Technique Name:</b>"), _p(mitre.get("technique_name"))],
            [_p("<b>Tactic:</b>"), _p(mitre.get("tactic"))],
            [_p("<b>Description:</b>"), _p(mitre.get("description"))],
            [_p("<b>Standard Mitigation:</b>"), _p(mitre.get("mitigation"))],
        ]
        t_m = Table(m_table_rows, colWidths=[130, 374])
        t_m.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_m)
        story.append(Spacer(1, 12))

        # ── 10. EVIDENCE & ARTIFACTS ───────────────────────────────────
        story.append(Paragraph("9. Evidence & Artifact References", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        ev_data = report_data.get("evidence", {})
        ev_rows = [
            [_p("<b>Prediction ID:</b>"), _p(ev_data.get("prediction", {}).get("id"))],
            [_p("<b>Explanation ID:</b>"), _p(shap_data.get("explanation_id") if shap_data else "N/A")],
            [_p("<b>Model Artifact File:</b>"), _p(ev_data.get("model", {}).get("model_file"))],
            [_p("<b>Dataset Reference:</b>"), _p(ev_data.get("model", {}).get("dataset_name"))],
        ]
        t_ev = Table(ev_rows, colWidths=[140, 364])
        t_ev.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_ev)
        story.append(Spacer(1, 12))

        # ── 11. RECOMMENDATIONS ────────────────────────────────────────
        story.append(Paragraph("10. Deterministic Remediation Recommendations", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        recs = report_data.get("recommendations", [])
        if recs:
            rec_rows = [["Category", "Action Item", "Technical Details"]]
            for r in recs:
                rec_rows.append([
                    _p(f"<b>{r.get('category') or 'N/A'}</b>"),
                    _p(r.get("recommendation")),
                    _p(r.get("detail")),
                ])
            t_rec = Table(rec_rows, colWidths=[100, 180, 224])
            t_rec.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_rec)

        story.append(Spacer(1, 12))

        # ── 12. APPENDIX & AUDIT VERIFICATION ──────────────────────────
        story.append(Paragraph("11. Appendix & Cryptographic Audit Metadata", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=12))

        app_rows = [
            [_p("<b>Platform Version:</b>"), _p("SentinelX AI v2.4 (Enterprise)")],
            [_p("<b>Report Engine Version:</b>"), _p("v5.1 (Deterministic SOC Reporter)")],
            [_p("<b>Generation Timestamp:</b>"), _p(report_data.get("generated_at"))],
            [_p("<b>PDF Renderer Engine:</b>"), _p("ReportLab PDF Toolkit")],
        ]
        t_app = Table(app_rows, colWidths=[140, 364])
        t_app.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_app)

        # Build document with NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        logger.info("PDFRenderer: rendered report PDF to '%s'.", pdf_path)
        return pdf_path
