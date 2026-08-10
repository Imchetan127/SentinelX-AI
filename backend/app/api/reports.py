"""app/api/reports.py — REST API Router for Enterprise Incident Reporting Engine.

Endpoints:
  - POST /api/v1/reports/generate/{incident_id}  (RBAC: Admin, Security Analyst)
  - GET  /api/v1/reports/{report_id}/download      (Download PDF)
  - GET  /api/v1/reports/                           (List reports)
  - GET  /api/v1/reports/{report_id}               (Report details)
  - POST /api/v1/reports/{report_id}/verify        (Verify SHA256 integrity)
"""
import os
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.reporting.service import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_user)],
)

ALLOWED_GENERATE_ROLES = {"admin", "security_analyst", "analyst", "soc_analyst"}


def _verify_generate_rbac(current_user: dict) -> None:
    """Enforce that only Admin or Security Analyst roles may generate reports."""
    role = (current_user.get("role") or "").lower().strip()
    if role not in ALLOWED_GENERATE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": f"Role '{role}' is not permitted to generate security incident reports. Required: Admin or Security Analyst.",
            },
        )


@router.post("/incidents/{incident_id}")
@router.post("/generate/{incident_id}")
def generate_report_api(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Generate, render, hash, persist, and audit a PDF report for an incident.

    RBAC: Restricted to Admin or Security Analyst roles.
    """
    _verify_generate_rbac(current_user)

    user_uuid = UUID(current_user["id"]) if current_user.get("id") else None
    service = ReportService(db)

    try:
        report = service.generate_report(incident_id=incident_id, user_id=user_uuid)
        return {
            "success": True,
            "data": {
                "id": str(report.id),
                "incident_id": str(report.incident_id),
                "title": report.title,
                "pdf_path": report.pdf_path,
                "sha256_hash": report.sha256_hash,
                "version": report.version,
                "generated_by": str(report.created_by) if report.created_by else None,
                "created_at": report.created_at.isoformat() if report.created_at else None,
            },
        }
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"Report generation failed: {str(exc)}"},
        )


@router.get("")
@router.get("/")
def list_reports_api(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """List generated incident reports (paginated)."""
    service = ReportService(db)
    try:
        records = service.list_reports(limit=limit, offset=offset)
        items = [
            {
                "id": str(r.id),
                "incident_id": str(r.incident_id),
                "title": r.title or r.summary,
                "pdf_path": r.pdf_path or r.recommendations,
                "sha256_hash": r.sha256_hash,
                "version": r.version,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
        return {"success": True, "count": len(items), "data": items}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc)},
        )


@router.get("/{report_id}")
def get_report_details_api(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Retrieve metadata details of a specific report."""
    service = ReportService(db)
    report = service.get_report(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": f"Report '{report_id}' not found."},
        )

    return {
        "success": True,
        "data": {
            "id": str(report.id),
            "incident_id": str(report.incident_id),
            "title": report.title or report.summary,
            "pdf_path": report.pdf_path or report.recommendations,
            "sha256_hash": report.sha256_hash,
            "version": report.version,
            "generated_by": str(report.created_by) if report.created_by else None,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        },
    }


@router.get("/{report_id}/download")
def download_report_api(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Download/stream the generated PDF file for a report. Logs REPORT_DOWNLOADED."""
    user_uuid = UUID(current_user["id"]) if current_user.get("id") else None
    service = ReportService(db)

    try:
        pdf_path, filename = service.download_report(report_id=report_id, user_id=user_uuid)
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc)},
        )


@router.post("/{report_id}/verify")
def verify_report_integrity_api(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Recompute SHA256 hash of PDF on disk and verify against stored DB hash (VALID vs TAMPERED)."""
    service = ReportService(db)
    try:
        result = service.verify_report_integrity(report_id)
        return {"success": True, "data": result}
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc)},
        )
