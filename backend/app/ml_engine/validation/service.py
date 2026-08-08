"""ValidationService — top-level orchestrator for Sprint 3.5.

Responsibilities
----------------
- Discover eligible models from the registry.
- Coordinate BenchmarkEngine for per-model validation.
- Persist ValidationResult rows via ValidationRepository.
- Emit all required audit events via AuditService.
- Coordinate ComparisonEngine for multi-model benchmarking.
- Return structured results to the API layer.

Does NOT modify inference logic, retrain models, or mutate the registry.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.ml_engine.validation.benchmark import BenchmarkEngine
from app.ml_engine.validation.comparison import ComparisonEngine
from app.ml_engine.validation.loader import ModelLoader
from app.ml_engine.validation.threshold import DEFAULT_THRESHOLDS
from app.models.validation_result import ValidationResult
from app.repositories.validation_repository import ValidationRepository
from app.services.audit_service import AuditService

logger = logging.getLogger("Validation.Service")

VALIDATOR_VERSION = "1.0.0"


class ValidationService:
    """Top-level orchestrator for the AI Validation & Benchmarking framework."""

    def __init__(
        self,
        db:            Session,
        base_dir:      str = "../models",
        datasets_dir:  str = "../datasets",
        n_folds:       int = 5,
        thresholds:    Optional[Dict[str, float]] = None,
        label_column:  str = "Label",
    ):
        self.db           = db
        self.base_dir     = base_dir
        self.datasets_dir = datasets_dir
        self.thresholds   = thresholds or DEFAULT_THRESHOLDS
        self.label_column = label_column
        self.n_folds      = n_folds

        self.loader     = ModelLoader(base_dir=base_dir, datasets_dir=datasets_dir)
        self.engine     = BenchmarkEngine(
            base_dir=base_dir,
            datasets_dir=datasets_dir,
            n_folds=n_folds,
            thresholds=self.thresholds,
            label_column=label_column,
        )
        self.comparison = ComparisonEngine()
        self.val_repo   = ValidationRepository(db)
        self.audit      = AuditService(db)

    # ------------------------------------------------------------------
    # Single-model validation
    # ------------------------------------------------------------------

    def validate_model(
        self,
        model_id: str,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Validate a specific model by its registry model_id string.

        Returns the full result dict with report, metrics, and quality gate.
        Persists a ValidationResult row and emits audit events.
        """
        logger.info("ValidationService: starting validation for model ID '%s'", model_id)

        # ── Audit: STARTED ────────────────────────────────────────────────
        self.audit.log_action(
            user_id=user_id,
            action="MODEL_VALIDATION_STARTED",
            resource="Model",
            resource_id=None,
            ip_address="127.0.0.1",
            status="started",
            details=f"Validation initiated for model ID '{model_id}'.",
        )

        # ── Locate registry entry ─────────────────────────────────────────
        model_meta = self.loader.get_model_meta(model_id)
        if not model_meta:
            msg = f"Model '{model_id}' not found in registry."
            logger.error(msg)
            raise FileNotFoundError(msg)

        status = (model_meta.get("status") or "").upper()
        if status in ("FAILED", "ARCHIVED"):
            raise ValueError(
                f"Model '{model_id}' has status '{status}' — not eligible for validation."
            )

        # ── Run benchmark pipeline ────────────────────────────────────────
        result = self.engine.validate_model(model_meta)

        # ── Persist ───────────────────────────────────────────────────────
        vr = self._persist_result(model_id, model_meta, result)

        # ── Audit: gate verdict ───────────────────────────────────────────
        gate_result = (result.get("quality_gate") or {}).get("result", "FAILED")
        audit_action = (
            "QUALITY_GATE_PASSED" if gate_result == "PASSED" else "QUALITY_GATE_FAILED"
        )
        self.audit.log_action(
            user_id=user_id,
            action=audit_action,
            resource="Model",
            resource_id=None,
            ip_address="127.0.0.1",
            status="success" if gate_result == "PASSED" else "failed",
            details=(
                f"Model '{model_id}' quality gate: {gate_result}. "
                f"Reasons: {result.get('quality_gate', {}).get('reasons', [])}"
            ),
        )

        # ── Audit: COMPLETED ──────────────────────────────────────────────
        self.audit.log_action(
            user_id=user_id,
            action="MODEL_VALIDATION_COMPLETED",
            resource="Model",
            resource_id=None,
            ip_address="127.0.0.1",
            status="success",
            details=f"Validation completed for model '{model_id}'. Result ID: {vr.id}.",
        )

        result["validation_result_id"] = str(vr.id)
        return result

    # ------------------------------------------------------------------
    # Full benchmark (all eligible models)
    # ------------------------------------------------------------------

    def run_benchmark(
        self,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Validate all eligible registry models and produce a comparison report.

        Models with status FAILED or ARCHIVED are skipped.
        Each model is validated independently — one model failure does not
        abort the rest of the benchmark run.
        """
        logger.info("ValidationService: starting full benchmark run.")

        eligible = self.loader.get_eligible_models()
        if not eligible:
            return {
                "total_eligible": 0,
                "results": [],
                "comparison": {},
                "skipped": [],
                "warnings": ["No eligible models found in registry."],
            }

        all_results: List[Dict[str, Any]] = []
        skipped: List[str] = []

        for model_meta in eligible:
            mid = model_meta.get("model_id", "?")
            try:
                res = self.validate_model(mid, user_id=user_id)
                all_results.append(res)
            except Exception as exc:
                logger.warning(
                    "Benchmark: model '%s' failed validation — skipping. Error: %s", mid, exc
                )
                skipped.append(f"Model '{mid}': {exc}")

        # ── Comparison ────────────────────────────────────────────────────
        comparison = {}
        if all_results:
            comparison = self.comparison.compare(all_results)
            self.audit.log_action(
                user_id=user_id,
                action="BENCHMARK_COMPLETED",
                resource="ValidationBenchmark",
                resource_id=None,
                ip_address="127.0.0.1",
                status="success",
                details=(
                    f"Benchmark complete. {len(all_results)} models validated; "
                    f"{len(skipped)} skipped."
                ),
            )

        logger.info(
            "Benchmark complete. %d validated, %d skipped.", len(all_results), len(skipped)
        )
        return {
            "total_eligible": len(eligible),
            "results":        all_results,
            "comparison":     comparison,
            "skipped":        skipped,
            "warnings":       skipped,
        }

    # ------------------------------------------------------------------
    # History queries (delegated to repository)
    # ------------------------------------------------------------------

    def list_results(self, limit: int = 50, offset: int = 0) -> List[ValidationResult]:
        """Return recent validation results from the database."""
        return self.val_repo.list_recent(limit=limit, offset=offset)

    def get_latest_for_model(self, model_id: str) -> Optional[ValidationResult]:
        """Return the most recent ValidationResult for *model_id*."""
        return self.val_repo.get_latest_for_model(model_id)

    def get_result_by_id(self, result_id: UUID) -> Optional[ValidationResult]:
        """Return a specific ValidationResult by primary key."""
        return self.val_repo.get(result_id)

    # ------------------------------------------------------------------
    # Internal: persist a validation result row
    # ------------------------------------------------------------------

    def _persist_result(
        self,
        model_id: str,
        model_meta: Dict[str, Any],
        result: Dict[str, Any],
    ) -> ValidationResult:
        """Create and commit a ValidationResult row."""
        gate       = result.get("quality_gate") or {}
        cv         = result.get("cv_results")  or {}

        # Resolve the DB model UUID
        try:
            model_uuid = UUID(model_id)
        except ValueError:
            model_uuid = None

        vr = ValidationResult(
            model_id            = model_uuid,
            validator_version   = VALIDATOR_VERSION,
            dataset_version     = model_meta.get("dataset_version"),
            pipeline_version    = model_meta.get("preprocessing_version"),
            metrics             = result.get("metrics"),
            cv_metrics          = cv.get("results"),
            threshold_results   = gate.get("threshold_results"),
            quality_gate_result = gate.get("result", "FAILED"),
            quality_gate_reasons= gate.get("reasons", []),
            report              = result.get("report"),
            warnings            = result.get("warnings", []),
            validated_at        = datetime.now(timezone.utc),
        )

        try:
            self.val_repo.add(vr)
            self.db.commit()
            self.db.refresh(vr)
            logger.info(
                "Persisted ValidationResult %s for model '%s'.", vr.id, model_id
            )
        except Exception as exc:
            self.db.rollback()
            logger.error("Failed to persist ValidationResult: %s", exc)
            raise

        return vr
