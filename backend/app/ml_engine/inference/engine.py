import os
import time
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import pandas as pd
import numpy as np
import joblib
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.model import Model
from app.models.enums import ModelStatus
from app.models.detection import Detection
from app.models.prediction import Prediction
from app.models.dataset import Dataset
from app.services.audit_service import AuditService

logger = logging.getLogger("ModelInference.Engine")


class InferenceService:
    # Class-level caches to share model/scaler instances across requests
    _cached_model_id: Optional[str] = None
    _cached_model: Any = None
    _cached_scaler: Any = None
    _cached_feature_names: List[str] = []

    def __init__(self, db: Session, base_dir: str = "../models", datasets_dir: str = "../datasets"):
        self.db = db
        self.base_dir = base_dir
        self.datasets_dir = datasets_dir
        self.registry_filepath = os.path.join(base_dir, "registry", "registry.json")
        self.audit_service = AuditService(db)

    def _resolve_active_model(self) -> Dict[str, Any]:
        # 1. Resolve active model from Model Registry
        if not os.path.exists(self.registry_filepath):
            self.audit_service.log_action(
                user_id=None,
                action="MISSING_MODEL",
                resource="ModelRegistry",
                resource_id=None,
                ip_address="127.0.0.1",
                status="failure",
                details="Model registry metadata database does not exist on disk."
            )
            raise RuntimeError("No model registry database exists. Please train a model first.")

        try:
            with open(self.registry_filepath, "r") as f:
                registry = json.load(f)
        except Exception as e:
            self.audit_service.log_action(
                user_id=None,
                action="PREDICTION_FAILED",
                resource="ModelRegistry",
                resource_id=None,
                ip_address="127.0.0.1",
                status="failure",
                details=f"Registry corruption: Failed to parse registry JSON. Error: {str(e)}"
            )
            raise RuntimeError(f"Corrupt model registry file: {str(e)}")

        if not registry:
            self.audit_service.log_action(
                user_id=None,
                action="MISSING_MODEL",
                resource="ModelRegistry",
                resource_id=None,
                ip_address="127.0.0.1",
                status="failure",
                details="No models registered in the Model Registry."
            )
            raise RuntimeError("No models registered in registry database.")

        # Check for model explicitly marked "PRODUCTION"
        active_model = next((m for m in registry if m.get("status") == "PRODUCTION"), None)
        
        # Fallback to model marked "ACTIVE"
        if not active_model:
            active_model = next((m for m in registry if m.get("status") == "ACTIVE"), None)

        # Fallback to READY (for backward-compatibility with older tests)
        if not active_model:
            ready_models = [m for m in registry if m.get("status") == "READY"]
            if ready_models:
                active_model = ready_models[-1]

        if not active_model:
            self.audit_service.log_action(
                user_id=None,
                action="MISSING_MODEL",
                resource="ModelRegistry",
                resource_id=None,
                ip_address="127.0.0.1",
                status="failure",
                details="Registry contains registered models, but none are marked PRODUCTION, ACTIVE or READY."
            )
            raise RuntimeError("No active or ready model resolved in the registry database.")

        return active_model

    def _get_model_and_scaler(self, model_meta: Dict[str, Any]) -> Tuple[Any, Any, List[str]]:
        model_id = model_meta["model_id"]
        
        # 2. Performance: Cache check and invalidation logic
        if (
            InferenceService._cached_model_id == model_id and
            InferenceService._cached_model is not None and
            InferenceService._cached_scaler is not None
        ):
            return InferenceService._cached_model, InferenceService._cached_scaler, InferenceService._cached_feature_names

        # Cache Invalidation / Load new model from disk
        logger.info(f"Cache miss or invalidation. Loading active model ID: {model_id}")
        
        # Verify model artifact file exists
        storage_path = model_meta.get("storage_path")
        if not storage_path or not os.path.exists(storage_path):
            self.audit_service.log_action(
                user_id=None,
                action="PREDICTION_FAILED",
                resource="Model",
                resource_id=UUID(model_id) if model_id else None,
                ip_address="127.0.0.1",
                status="failure",
                details=f"Model artifact binary not found at storage path: {storage_path}"
            )
            raise FileNotFoundError(f"Model binary artifact missing at: {storage_path}")

        # Verify scaler artifact exists in datasets/processed
        dataset_ver = model_meta.get("dataset_version", "cicids_test_v1.0")
        
        # Determine dataset name & version parameters safely
        if "_" in dataset_ver:
            dataset_name = dataset_ver.split("_")[0]
            dataset_version = dataset_ver.split("_")[1]
        else:
            dataset_name = "cicids_test"
            dataset_version = dataset_ver

        scaler_filename = f"{dataset_name}_{dataset_version}_scaler.joblib"
        scaler_filepath = os.path.join(self.datasets_dir, "processed", scaler_filename)
        
        if not os.path.exists(scaler_filepath):
            self.audit_service.log_action(
                user_id=None,
                action="PREDICTION_FAILED",
                resource="Scaler",
                resource_id=UUID(model_id) if model_id else None,
                ip_address="127.0.0.1",
                status="failure",
                details=f"Preprocessing scaler binary not found at path: {scaler_filepath}"
            )
            raise FileNotFoundError(f"Preprocessing scaler artifact missing at: {scaler_filepath}")

        # Resolve expected features from the processed dataset header columns to avoid feature mismatches
        train_filename = f"{dataset_name}_{dataset_version}_train.csv"
        train_filepath = os.path.join(self.datasets_dir, "processed", train_filename)
        
        if not os.path.exists(train_filepath):
            raise FileNotFoundError(f"Train split file missing to resolve feature order: {train_filepath}")

        try:
            cols = list(pd.read_csv(train_filepath, nrows=0).columns)
            feature_names = [c for c in cols if c != "Label"]
        except Exception as e:
            raise ValueError(f"Failed to infer feature columns from training file: {str(e)}")

        # Deserialize model and scaler
        try:
            model = joblib.load(storage_path)
            scaler = joblib.load(scaler_filepath)
        except Exception as e:
            self.audit_service.log_action(
                user_id=None,
                action="PREDICTION_FAILED",
                resource="Model",
                resource_id=UUID(model_id) if model_id else None,
                ip_address="127.0.0.1",
                status="failure",
                details=f"Model corruption: joblib deserialization failed. Error: {str(e)}"
            )
            raise RuntimeError(f"Corrupted model or scaler files: {str(e)}")

        # Store in Class-level caches
        InferenceService._cached_model_id = model_id
        InferenceService._cached_model = model
        InferenceService._cached_scaler = scaler
        InferenceService._cached_feature_names = feature_names

        self.audit_service.log_action(
            user_id=None,
            action="MODEL_LOADED",
            resource="Model",
            resource_id=UUID(model_id) if model_id else None,
            ip_address="127.0.0.1",
            status="success",
            details=f"Model successfully loaded and cached in-memory: {model_meta['algorithm']} v{model_meta['version']}"
        )

        return model, scaler, feature_names

    def _sync_model_to_db(self, model_meta: Dict[str, Any]) -> Model:
        model_id = UUID(model_meta["model_id"])
        db_model = self.db.get(Model, model_id)
        if db_model:
            return db_model

        # Model not in DB yet; let's create a default dataset if none exists, then create the Model row
        dataset = self.db.scalars(select(Dataset)).first()
        if not dataset:
            dataset = Dataset(name="default_dataset", version="1.0")
            self.db.add(dataset)
            self.db.flush()

        db_model = Model(
            id=model_id,
            dataset_id=dataset.id,
            algorithm=model_meta["algorithm"],
            version=model_meta["version"],
            accuracy=model_meta["metrics"].get("accuracy", 0.0),
            precision=model_meta["metrics"].get("precision", 0.0),
            recall=model_meta["metrics"].get("recall", 0.0),
            f1_score=model_meta["metrics"].get("f1_score", 0.0),
            training_duration=model_meta["metrics"].get("training_time_sec"),
            feature_count=model_meta.get("feature_count"),
            hyperparameters=model_meta.get("hyperparameters"),
            model_file=model_meta["storage_path"],
            status=ModelStatus.VALIDATED
        )
        self.db.add(db_model)
        self.db.flush()
        return db_model

    def validate_features(self, features_dict: Dict[str, Any], expected_features: List[str]) -> List[str]:
        # Perform feature count, order, numeric type, NaN, and infinite checks
        validation_errors = []

        # Check missing features
        for f in expected_features:
            if f not in features_dict:
                validation_errors.append(f"Missing feature column: '{f}'")

        # Check unexpected features
        for f in features_dict.keys():
            if f not in expected_features:
                validation_errors.append(f"Unsupported unexpected feature column: '{f}'")

        if validation_errors:
            return validation_errors

        # Check types, NaNs, and infinite values
        for f in expected_features:
            val = features_dict[f]
            # Verify numeric types
            if not isinstance(val, (int, float, np.number)):
                validation_errors.append(f"Non-numeric data type in column '{f}': {type(val).__name__}")
                continue
            
            # Check NaN
            if pd.isna(val) or np.isnan(val):
                validation_errors.append(f"NaN / missing value detected in feature column '{f}'")

            # Check Inf
            if np.isinf(val):
                validation_errors.append(f"Infinite value detected in feature column '{f}'")

        return validation_errors

    def predict_raw(
        self,
        features_dict: Dict[str, Any],
        detection_id: UUID,
        user_id: Optional[UUID] = None,
        ip_address: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        t_start = time.perf_counter()

        # Check if the validation_id is valid
        detection = self.db.get(Detection, detection_id)
        if not detection:
            raise ValueError(f"Detection ID '{detection_id}' does not exist in database.")

        try:
            # 1. Resolve active model from registry
            model_meta = self._resolve_active_model()
            model_id = UUID(model_meta["model_id"])

            # Sync model config row to database if not present
            self._sync_model_to_db(model_meta)

            # 2. Get model and scaler instance (caching handled inside)
            model, scaler, expected_features = self._get_model_and_scaler(model_meta)

            # 3. Validate features
            errors = self.validate_features(features_dict, expected_features)
            if errors:
                self.audit_service.log_action(
                    user_id=user_id,
                    action="VALIDATION_FAILED",
                    resource="Model",
                    resource_id=model_id,
                    ip_address=ip_address,
                    status="failure",
                    details=f"Feature validation failed: {'; '.join(errors)}"
                )
                raise ValueError(f"Feature validation failed: {errors}")

            # 4. Preprocessing: apply scaler to the ordered features
            # Reconstruct row dataframe in the exact expected feature order
            row_df = pd.DataFrame([features_dict], columns=expected_features)
            
            if scaler is not None:
                scaled_array = scaler.transform(row_df)
                scaled_df = pd.DataFrame(scaled_array, columns=expected_features)
            else:
                scaled_df = row_df

            # 5. Prediction
            y_pred = model.predict(scaled_df)[0]
            
            # Extract probabilities
            confidence = 0.0
            probability = 0.0
            if hasattr(model, "predict_proba"):
                probas = model.predict_proba(scaled_df)[0]
                # Binomial confidence logic
                confidence = float(probas[y_pred])
                probability = float(probas[1]) if len(probas) > 1 else float(probas[0])
            else:
                confidence = 1.0
                probability = 1.0 if y_pred == 1 else 0.0

            prediction_label = "malicious" if y_pred == 1 else "clean"
            duration_sec = time.perf_counter() - t_start

            # 6. Persist prediction to the database
            db_prediction = Prediction(
                detection_id=detection_id,
                model_id=model_id,
                prediction=prediction_label,
                confidence=confidence,
                probability=probability,
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(db_prediction)
            self.db.commit()

            # 7. Audit log
            self.audit_service.log_action(
                user_id=user_id,
                action="PREDICTION_EXECUTED",
                resource="Prediction",
                resource_id=db_prediction.id,
                ip_address=ip_address,
                status="success",
                details=f"Inference execution completed. Label: {prediction_label} [Conf: {confidence:.2f}]"
            )

            return {
                "prediction_id": str(db_prediction.id),
                "prediction": prediction_label,
                "confidence": round(confidence, 4),
                "probability": round(probability, 4),
                "model_version": model_meta["version"],
                "algorithm": model_meta["algorithm"],
                "prediction_timestamp": db_prediction.created_at.isoformat(),
                "duration_ms": round(duration_sec * 1000, 3)
            }

        except Exception as e:
            # Audit prediction failure
            self.audit_service.log_action(
                user_id=user_id,
                action="PREDICTION_FAILED",
                resource="Prediction",
                resource_id=None,
                ip_address=ip_address,
                status="failure",
                details=f"Inference pipeline execution crashed. Error: {str(e)}"
            )
            # Re-raise to let controllers return structured validation errors
            raise e

    def run_model_inference(self, model_file: str, payload_data: Any) -> Dict[str, Any]:
        """
        Run real model inference against trained .bin / .joblib model artifacts stored in backend/models/.
        Uses domain-matched features extracted via app.ml_engine.features.extract_features_dict.
        """
        from app.ml_engine.features import extract_features_dict, FEATURE_NAMES

        models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models"))
        model_path = os.path.join(models_dir, model_file)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model binary artifact '{model_file}' missing at path: {model_path}")

        model = joblib.load(model_path)
        feat_dict = extract_features_dict(payload_data)
        df = pd.DataFrame([feat_dict], columns=FEATURE_NAMES)

        if hasattr(model, "predict_proba"):
            probas = model.predict_proba(df)[0]
            prob = float(probas[1]) if len(probas) > 1 else float(probas[0])
            
            # Security-tuned per-model operating thresholds (STEP 3)
            model_file_lower = model_file.lower()
            if "rf" in model_file_lower or "random" in model_file_lower:
                model_th = 0.35
            elif "lgb" in model_file_lower or "lightgbm" in model_file_lower:
                model_th = 0.40
            elif "xgb" in model_file_lower or "xgboost" in model_file_lower:
                model_th = 0.40
            else:
                model_th = 0.50

            label = "malicious" if prob >= model_th else "clean"
            conf = prob if label == "malicious" else (1.0 - prob)
        elif hasattr(model, "decision_function"):
            score = float(model.decision_function(df)[0])
            iso_pred = model.predict(df)[0]
            label = "malicious" if iso_pred == -1 else "clean"
            conf = float(min(0.99, max(0.05, 0.5 - (score * 2.5)))) if iso_pred == -1 else float(min(0.99, max(0.05, 0.5 + (score * 2.5))))
            prob = conf if label == "malicious" else (1.0 - conf)
        else:
            y_pred = model.predict(df)[0]
            label = "malicious" if y_pred == 1 else "clean"
            conf = 0.95
            prob = 0.95 if label == "malicious" else 0.05

        return {
            "prediction": label,
            "confidence": round(conf, 4),
            "probability": round(prob, 4),
            "features": feat_dict
        }

