"""app/reporting/integrity.py — SHA256 Hashing & Report Integrity Verifier.

Computes and verifies cryptographic SHA256 hashes of generated report PDFs.
Detects any file tampering or file corruption post-generation.
"""
import hashlib
import os
import logging
from typing import Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.report import Report

logger = logging.getLogger("Reporting.Integrity")


class ReportIntegrityVerifier:
    """Computes SHA256 hashes and verifies PDF file integrity against stored database records."""

    @staticmethod
    def compute_sha256(file_path: str) -> str:
        """Compute SHA256 hex digest for a file on disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Report file not found at: {file_path}")

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)

        return sha256.hexdigest()

    def verify_report(self, db: Session, report_id: UUID) -> Dict[str, Any]:
        """Verify report PDF integrity against stored SHA256 hash in database."""
        report = db.get(Report, report_id)
        if report is None:
            raise FileNotFoundError(f"Report record '{report_id}' not found in database.")

        pdf_path = report.pdf_path or report.recommendations
        if not pdf_path or not os.path.exists(pdf_path):
            return {
                "status": "TAMPERED",
                "report_id": str(report.id),
                "reason": f"PDF file missing from storage path: {pdf_path}",
                "stored_hash": report.sha256_hash,
                "computed_hash": None,
                "is_valid": False,
            }

        computed_hash = self.compute_sha256(pdf_path)
        stored_hash = report.sha256_hash

        if stored_hash and computed_hash == stored_hash:
            logger.info("ReportIntegrityVerifier: report '%s' verified VALID.", report_id)
            return {
                "status": "VALID",
                "report_id": str(report.id),
                "pdf_path": pdf_path,
                "stored_hash": stored_hash,
                "computed_hash": computed_hash,
                "is_valid": True,
            }
        else:
            logger.warning("ReportIntegrityVerifier: report '%s' TAMPERED! stored=%s computed=%s", report_id, stored_hash, computed_hash)
            return {
                "status": "TAMPERED",
                "report_id": str(report.id),
                "pdf_path": pdf_path,
                "stored_hash": stored_hash,
                "computed_hash": computed_hash,
                "is_valid": False,
            }
