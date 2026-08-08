import os
import json
import shutil
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.model import Model
from app.models.enums import ModelStatus
from app.models.dataset import Dataset
from app.services.audit_service import AuditService

logger = logging.getLogger("ModelGovernance.Service")

# Valid lifecycle transition paths (directed state graph)
ALLOWED_TRANSITIONS = {
    ModelStatus.TRAINING:   [ModelStatus.VALIDATED, ModelStatus.FAILED],
    ModelStatus.VALIDATED:  [ModelStatus.STAGING, ModelStatus.PRODUCTION, ModelStatus.ARCHIVED, ModelStatus.FAILED],
    ModelStatus.STAGING:    [ModelStatus.PRODUCTION, ModelStatus.ARCHIVED, ModelStatus.FAILED],
    ModelStatus.PRODUCTION: [ModelStatus.STAGING, ModelStatus.ARCHIVED, ModelStatus.FAILED],
    ModelStatus.ARCHIVED:   [ModelStatus.STAGING, ModelStatus.PRODUCTION],
    ModelStatus.FAILED:     [],   # terminal – no further transitions permitted
}

# Mandatory fields that every registry entry must carry
REQUIRED_REGISTRY_FIELDS = {
    "model_id", "algorithm", "version",
    "metrics", "storage_path", "status",
}

# Default configurable minimum promotion thresholds for PRODUCTION gate
DEFAULT_MIN_ACCURACY = 0.70
DEFAULT_MIN_F1_SCORE = 0.65


def _safe_parse_status(raw: Optional[str], default: ModelStatus = ModelStatus.VALIDATED) -> ModelStatus:
    """Safely parse a status string into a ModelStatus enum.

    Falls back to *default* for unknown or legacy values (e.g. the removed
    'READY' literal) so that callers never receive a KeyError.
    """
    if not raw:
        return default
    try:
        return ModelStatus[raw.upper()]
    except KeyError:
        logger.warning(
            "Unknown ModelStatus string '%s' in registry — treating as %s.",
            raw, default.value
        )
        return default


class ModelGovernanceService:
    def __init__(
        self,
        db: Session,
        base_dir: str = "../models",
        datasets_dir: str = "../datasets",
        min_accuracy: float = DEFAULT_MIN_ACCURACY,
        min_f1_score: float = DEFAULT_MIN_F1_SCORE,
    ):
        self.db = db
        self.base_dir = base_dir
        self.datasets_dir = datasets_dir
        self.registry_filepath = os.path.join(base_dir, "registry", "registry.json")
        self.audit_service = AuditService(db)
        # Configurable minimum promotion thresholds
        self.min_accuracy = min_accuracy
        self.min_f1_score = min_f1_score

    # ------------------------------------------------------------------
    # Registry I/O helpers
    # ------------------------------------------------------------------

    def _load_registry(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.registry_filepath):
            return []
        try:
            with open(self.registry_filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Corrupt model registry JSON database: {str(e)}")

    def _save_registry(self, registry: List[Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self.registry_filepath), exist_ok=True)
        # Write atomically via a temp file + rename to avoid partial writes
        tmp_path = self.registry_filepath + ".tmp"
        try:
            with open(tmp_path, "w") as f:
                json.dump(registry, f, indent=4)
            shutil.move(tmp_path, self.registry_filepath)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise RuntimeError(f"Failed to write model registry: {str(e)}")

    # ------------------------------------------------------------------
    # Active model resolution
    # ------------------------------------------------------------------

    def get_active_model(self) -> Dict[str, Any]:
        """Return the registry entry for the current PRODUCTION model.

        Raises RuntimeError when no PRODUCTION model exists.
        """
        registry = self._load_registry()
        active = next((m for m in registry if m.get("status") == "PRODUCTION"), None)
        if not active:
            raise RuntimeError(
                "No PRODUCTION model found in the registry. "
                "Promote a VALIDATED or STAGING model first."
            )
        return active

    # ------------------------------------------------------------------
    # Startup validation
    # ------------------------------------------------------------------

    def startup_validation(self) -> Dict[str, Any]:
        logger.info("Initializing model registry startup validation checks…")

        if not os.path.exists(self.registry_filepath):
            return {"status": "OK", "message": "No model registry initialized yet."}

        registry = self._load_registry()
        diagnostics: Dict[str, Any] = {
            "total_registered_models": len(registry),
            "production_models_count": 0,
            "corrupt_models": [],
            "missing_artifacts": [],
            "db_mismatches": [],
        }

        for entry in registry:
            model_id_str = entry.get("model_id")

            # ── 1. Schema completeness check ──────────────────────────────
            missing_fields = REQUIRED_REGISTRY_FIELDS - set(entry.keys())
            if missing_fields:
                diagnostics["corrupt_models"].append(
                    f"Entry '{model_id_str or '?'}' is missing required fields: {sorted(missing_fields)}"
                )
                # Skip further checks for this corrupt entry
                continue

            if not model_id_str:
                diagnostics["corrupt_models"].append("Entry is missing model_id key.")
                continue

            # ── 2. Artifact existence ─────────────────────────────────────
            storage_path = entry.get("storage_path", "")
            if not storage_path or not os.path.exists(storage_path):
                diagnostics["missing_artifacts"].append(
                    f"Model '{model_id_str}' artifact missing at: {storage_path!r}"
                )

            # ── 3. Preprocessing scaler existence ────────────────────────
            dataset_ver = entry.get("dataset_version") or "cicids_test_v1.0"
            if "_" in dataset_ver:
                dataset_name, dataset_version = dataset_ver.split("_", 1)
            else:
                dataset_name, dataset_version = "cicids_test", dataset_ver
            scaler_filename = f"{dataset_name}_{dataset_version}_scaler.joblib"
            scaler_path = os.path.join(self.datasets_dir, "processed", scaler_filename)
            if not os.path.exists(scaler_path):
                diagnostics["missing_artifacts"].append(
                    f"Model '{model_id_str}' scaler missing at: {scaler_path!r}"
                )

            # ── 4. Production count ───────────────────────────────────────
            if entry.get("status") == "PRODUCTION":
                diagnostics["production_models_count"] += 1

            # ── 5. DB synchronization ─────────────────────────────────────
            try:
                model_uuid = UUID(model_id_str)
            except ValueError:
                diagnostics["corrupt_models"].append(
                    f"Entry has invalid UUID model_id: '{model_id_str}'"
                )
                continue

            db_model = self.db.get(Model, model_uuid)
            if not db_model:
                diagnostics["db_mismatches"].append(
                    f"Model '{model_id_str}' exists in registry but not in database."
                )
            else:
                registry_status = _safe_parse_status(entry.get("status"))
                if db_model.status != registry_status:
                    # Registry is the source of truth — sync the DB row
                    try:
                        db_model.status = registry_status
                        self.db.add(db_model)
                        self.db.flush()
                        logger.info(
                            "Startup sync: model '%s' DB status updated to %s.",
                            model_id_str, registry_status.value
                        )
                    except Exception as sync_err:
                        logger.warning(
                            "Failed to sync DB status for model '%s': %s",
                            model_id_str, sync_err
                        )

        self.db.commit()

        # ── 6. Single-production policy ───────────────────────────────────
        if diagnostics["production_models_count"] > 1:
            error_msg = (
                f"Startup Governance Failure: {diagnostics['production_models_count']} models "
                "are simultaneously PRODUCTION. The registry is in an illegal state."
            )
            logger.critical(error_msg)
            raise ValueError(error_msg)

        logger.info("Startup validation complete. Diagnostics: %s", diagnostics)
        return diagnostics

    # ------------------------------------------------------------------
    # Model Card
    # ------------------------------------------------------------------

    def get_model_card(self, model_id: UUID) -> Dict[str, Any]:
        registry = self._load_registry()
        model_meta = next(
            (m for m in registry if m.get("model_id") == str(model_id)), None
        )

        if not model_meta:
            db_model = self.db.get(Model, model_id)
            if not db_model:
                raise FileNotFoundError(
                    f"Model Card lookup failed: Model '{model_id}' not found."
                )
            model_meta = {
                "model_id": str(db_model.id),
                "algorithm": db_model.algorithm,
                "version": db_model.version,
                "dataset_version": "unknown",
                "preprocessing_version": "unknown",
                "training_timestamp": db_model.created_at.isoformat() if db_model.created_at else None,
                "metrics": {
                    "accuracy": db_model.accuracy,
                    "precision": db_model.precision,
                    "recall": db_model.recall,
                    "f1_score": db_model.f1_score,
                },
                "hyperparameters": db_model.hyperparameters or {},
                "status": db_model.status.value,
                "storage_path": db_model.model_file,
            }

        return {
            "model_id":          model_meta["model_id"],
            "algorithm":         model_meta["algorithm"],
            "version":           model_meta["version"],
            "dataset_version":   model_meta.get("dataset_version", "unknown"),
            "pipeline_version":  model_meta.get("preprocessing_version", "unknown"),
            "training_date":     model_meta.get("training_timestamp"),
            "metrics":           model_meta.get("metrics", {}),
            "hyperparameters":   model_meta.get("hyperparameters", {}),
            "intended_use":      model_meta.get(
                "intended_use",
                "SentinelX AI Network Threat Intrusion Analysis & Defense",
            ),
            "known_limitations": model_meta.get(
                "known_limitations",
                "Evaluated on CICIDS2017 synthetic streams. "
                "Performance under novel zero-days may decay.",
            ),
            "author":            model_meta.get(
                "author",
                "SentinelX MLOps Governance Architecture Board",
            ),
            "status":            model_meta.get("status", ModelStatus.VALIDATED.value),
            "artifact_path":     model_meta["storage_path"],
        }

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def validate_transition(
        self,
        current_status: ModelStatus,
        target_status: ModelStatus,
    ) -> None:
        if current_status == target_status:
            return
        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        if target_status not in allowed:
            raise ValueError(
                f"Illegal lifecycle transition: "
                f"'{current_status.value}' → '{target_status.value}'"
            )

    def _ensure_model_in_db(
        self, model_id: UUID, model_meta: Dict[str, Any], current_status: ModelStatus
    ) -> Model:
        """Return the DB row for *model_id*, creating it from registry data if absent."""
        db_model = self.db.get(Model, model_id)
        if db_model:
            return db_model

        dataset = self.db.scalars(select(Dataset)).first()
        if not dataset:
            dataset = Dataset(name="default_dataset", version="1.0")
            self.db.add(dataset)
            self.db.flush()

        metrics = model_meta.get("metrics") or {}
        db_model = Model(
            id=model_id,
            dataset_id=dataset.id,
            algorithm=model_meta["algorithm"],
            version=model_meta["version"],
            accuracy=metrics.get("accuracy", 0.0),
            precision=metrics.get("precision", 0.0),
            recall=metrics.get("recall", 0.0),
            f1_score=metrics.get("f1_score", 0.0),
            training_duration=metrics.get("training_time_sec"),
            feature_count=model_meta.get("feature_count"),
            hyperparameters=model_meta.get("hyperparameters"),
            model_file=model_meta["storage_path"],
            status=current_status,
        )
        self.db.add(db_model)
        self.db.flush()
        return db_model

    # ------------------------------------------------------------------
    # Promote
    # ------------------------------------------------------------------

    def promote_model(
        self,
        model_id: UUID,
        target_status: ModelStatus,
        user_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        logger.info(
            "Initiating promotion of model %s → %s", model_id, target_status.value
        )

        registry = self._load_registry()
        model_meta = next(
            (m for m in registry if m.get("model_id") == str(model_id)), None
        )
        if not model_meta:
            raise FileNotFoundError(
                f"Promotion failed: Model '{model_id}' not found in registry."
            )

        # Safe status parse — never raises KeyError on legacy "READY" values
        current_status = _safe_parse_status(model_meta.get("status"))
        self.validate_transition(current_status, target_status)

        # ── PRODUCTION approval gates ─────────────────────────────────────
        if target_status == ModelStatus.PRODUCTION:
            if current_status not in (ModelStatus.VALIDATED, ModelStatus.STAGING):
                raise ValueError(
                    f"Approval Policy: only VALIDATED or STAGING models may be promoted to "
                    f"PRODUCTION. Current status: {current_status.value}"
                )

            storage_path = model_meta.get("storage_path", "")
            if not storage_path or not os.path.exists(storage_path):
                raise ValueError(
                    f"Approval Policy: model artifact does not exist at: {storage_path!r}"
                )

            metrics = model_meta.get("metrics") or {}
            if "accuracy" not in metrics or "f1_score" not in metrics:
                raise ValueError(
                    "Approval Policy: registry entry is missing 'accuracy' or 'f1_score' metrics."
                )

            accuracy  = float(metrics.get("accuracy", 0.0))
            f1_score  = float(metrics.get("f1_score", 0.0))
            if accuracy < self.min_accuracy:
                raise ValueError(
                    f"Approval Policy: accuracy {accuracy:.4f} is below the minimum "
                    f"threshold of {self.min_accuracy:.4f}."
                )
            if f1_score < self.min_f1_score:
                raise ValueError(
                    f"Approval Policy: f1_score {f1_score:.4f} is below the minimum "
                    f"threshold of {self.min_f1_score:.4f}."
                )

            # Dataset lineage metadata must exist
            dataset_ver = model_meta.get("dataset_version") or "cicids_test_v1.0"
            if "_" in dataset_ver:
                d_name, d_version = dataset_ver.split("_", 1)
            else:
                d_name, d_version = "cicids_test", dataset_ver
            meta_file = os.path.join(
                self.datasets_dir, "metadata", f"{d_name}_{d_version}_metadata.json"
            )
            if not os.path.exists(meta_file):
                raise ValueError(
                    f"Approval Policy: dataset lineage metadata not found at: {meta_file!r}"
                )

        # ── Ensure model row exists in DB ─────────────────────────────────
        db_model = self._ensure_model_in_db(model_id, model_meta, current_status)

        action_map = {
            ModelStatus.VALIDATED:  "MODEL_VALIDATED",
            ModelStatus.STAGING:    "MODEL_STAGING",
            ModelStatus.PRODUCTION: "MODEL_PROMOTED",
            ModelStatus.ARCHIVED:   "MODEL_ARCHIVED",
            ModelStatus.FAILED:     "MODEL_FAILED",
        }

        try:
            # Demote previous PRODUCTION models (DB rows)
            if target_status == ModelStatus.PRODUCTION:
                prev_prod_rows = self.db.scalars(
                    select(Model).where(
                        Model.status == ModelStatus.PRODUCTION,
                        Model.id != model_id,
                    )
                ).all()
                for m in prev_prod_rows:
                    m.status = ModelStatus.STAGING
                    self.db.add(m)
                    self.audit_service.log_action(
                        user_id=user_id,
                        action="MODEL_DEMOTED",
                        resource="Model",
                        resource_id=m.id,
                        ip_address="127.0.0.1",
                        status="success",
                        details=(
                            f"Model ID '{m.id}' automatically demoted PRODUCTION → STAGING "
                            f"due to promotion of '{model_id}'."
                        ),
                    )

            # Update DB row
            db_model.status = target_status
            self.db.add(db_model)
            self.db.flush()

            # Log the primary audit event
            self.audit_service.log_action(
                user_id=user_id,
                action=action_map.get(target_status, "MODEL_STATUS_CHANGED"),
                resource="Model",
                resource_id=model_id,
                ip_address="127.0.0.1",
                status="success",
                details=(
                    f"Model ID '{model_id}' promoted to lifecycle state: "
                    f"{target_status.value}."
                ),
            )

            # ── Commit DB first, then persist registry ────────────────────
            self.db.commit()

            # Demote previous PRODUCTION entries in the registry JSON
            if target_status == ModelStatus.PRODUCTION:
                for entry in registry:
                    if (
                        entry.get("status") == "PRODUCTION"
                        and entry.get("model_id") != str(model_id)
                    ):
                        entry["status"] = "STAGING"

            model_meta["status"] = target_status.value
            self._save_registry(registry)   # atomic write via tmp+rename

        except Exception as exc:
            self.db.rollback()
            self.audit_service.log_action(
                user_id=user_id,
                action="MODEL_REJECTED",
                resource="Model",
                resource_id=model_id,
                ip_address="127.0.0.1",
                status="failure",
                details=f"Promotion transaction failed for model '{model_id}'. Error: {exc}",
            )
            raise RuntimeError(f"Atomic promotion failed: {exc}") from exc

        return model_meta

    # ------------------------------------------------------------------
    # Archive (convenience wrapper)
    # ------------------------------------------------------------------

    def archive_model(
        self, model_id: UUID, user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        return self.promote_model(model_id, ModelStatus.ARCHIVED, user_id)

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------

    def rollback_model(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        logger.info("Executing rollback to restore previous production model…")

        registry = self._load_registry()

        curr_prod = next(
            (m for m in registry if m.get("status") == "PRODUCTION"), None
        )

        candidates = [
            m for m in registry if m.get("status") in ("STAGING", "VALIDATED")
        ]
        if not candidates:
            raise ValueError(
                "Rollback failed: no STAGING or VALIDATED candidate found."
            )

        candidates.sort(
            key=lambda x: x.get("training_timestamp", ""), reverse=True
        )
        rollback_target = candidates[0]
        target_uuid = UUID(rollback_target["model_id"])

        logger.info(
            "Rollback target resolved: ID %s (%s v%s)",
            target_uuid, rollback_target["algorithm"], rollback_target["version"]
        )

        db_target = self.db.get(Model, target_uuid)
        if not db_target:
            target_status = _safe_parse_status(rollback_target.get("status"))
            self._ensure_model_in_db(target_uuid, rollback_target, target_status)
            db_target = self.db.get(Model, target_uuid)

        try:
            # Demote the current production model in the DB
            if curr_prod:
                curr_uuid = UUID(curr_prod["model_id"])
                db_curr = self.db.get(Model, curr_uuid)
                if db_curr:
                    db_curr.status = ModelStatus.STAGING
                    self.db.add(db_curr)
                self.audit_service.log_action(
                    user_id=user_id,
                    action="MODEL_DEMOTED",
                    resource="Model",
                    resource_id=curr_uuid,
                    ip_address="127.0.0.1",
                    status="success",
                    details=f"Model '{curr_uuid}' demoted PRODUCTION → STAGING during rollback.",
                )

            # Promote target model in the DB
            db_target.status = ModelStatus.PRODUCTION
            self.db.add(db_target)
            self.db.flush()

            self.audit_service.log_action(
                user_id=user_id,
                action="MODEL_ROLLED_BACK",
                resource="Model",
                resource_id=target_uuid,
                ip_address="127.0.0.1",
                status="success",
                details=(
                    f"Rollback successful: serving restored to model '{target_uuid}' "
                    f"({rollback_target['algorithm']} v{rollback_target['version']})."
                ),
            )

            # ── Commit DB first, then persist registry ────────────────────
            self.db.commit()

            if curr_prod:
                curr_prod["status"] = "STAGING"
            rollback_target["status"] = "PRODUCTION"
            self._save_registry(registry)   # atomic write via tmp+rename

        except Exception as exc:
            self.db.rollback()
            self.audit_service.log_action(
                user_id=user_id,
                action="MODEL_REJECTED",
                resource="Model",
                resource_id=target_uuid,
                ip_address="127.0.0.1",
                status="failure",
                details=f"Rollback transaction failed. Error: {exc}",
            )
            raise RuntimeError(f"Model rollback failed: {exc}") from exc

        return rollback_target

    # ------------------------------------------------------------------
    # DB-sync helper (used by rollback when row doesn't exist)
    # ------------------------------------------------------------------

    def _sync_model_to_db_single(self, model_meta: Dict[str, Any]) -> None:
        model_id = UUID(model_meta["model_id"])
        status = _safe_parse_status(model_meta.get("status"))   # never KeyError

        dataset = self.db.scalars(select(Dataset)).first()
        if not dataset:
            dataset = Dataset(name="default_dataset", version="1.0")
            self.db.add(dataset)
            self.db.flush()

        metrics = model_meta.get("metrics") or {}
        db_model = Model(
            id=model_id,
            dataset_id=dataset.id,
            algorithm=model_meta["algorithm"],
            version=model_meta["version"],
            accuracy=metrics.get("accuracy", 0.0),
            precision=metrics.get("precision", 0.0),
            recall=metrics.get("recall", 0.0),
            f1_score=metrics.get("f1_score", 0.0),
            training_duration=metrics.get("training_time_sec"),
            feature_count=model_meta.get("feature_count"),
            hyperparameters=model_meta.get("hyperparameters"),
            model_file=model_meta["storage_path"],
            status=status,
        )
        self.db.add(db_model)
        self.db.flush()
