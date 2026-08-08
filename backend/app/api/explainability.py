from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any, Dict, List, Optional

from app.database.session import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.ml_engine.explainability.service import ExplainabilityService
from app.ml_engine.explainability.shap_engine import UnsupportedModelError
from app.ml_engine.explainability.validator import ExplanationValidationError
from pydantic import BaseModel

router = APIRouter(
    prefix="/explain",
    tags=["Explainable AI (XAI)"],
)


class ExplainRequest(BaseModel):
    """Feature values required to reproduce the explanation (same dict used for inference)."""
    features: Dict[str, float]


# FIX-1: /history MUST be declared BEFORE /{prediction_id}.
# FastAPI matches routes in declaration order; a dynamic /{prediction_id}
# segment placed first would shadow any literal path like /history.
@router.get("/history")
def list_explanations_api(
    limit:  int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """List recent SHAP explanations (paginated)."""
    service = ExplainabilityService(
        db,
        base_dir=settings.MODEL_DIR,
        datasets_dir=settings.DATASETS_DIR,
    )
    try:
        records = service.list_recent(limit=limit, offset=offset)
        items = [
            {
                "id":              str(r.id),
                "prediction_id":   str(r.prediction_id),
                "algorithm":       r.algorithm,
                "model_version":   r.model_version,
                "prediction_label": r.prediction_label,
                "confidence":      r.confidence,
                "explained_at":    r.explained_at.isoformat() if r.explained_at else None,
            }
            for r in records
        ]
        return {"success": True, "count": len(items), "data": items}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc)},
        )


@router.post("/{prediction_id}")
def generate_explanation_api(
    prediction_id: UUID,
    body: ExplainRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Generate and persist a SHAP explanation for a specific prediction.

    The caller must supply the same feature dict that was used for the
    original inference call so that SHAP can reconstruct the scaled input.
    """
    service = ExplainabilityService(
        db,
        base_dir=settings.MODEL_DIR,
        datasets_dir=settings.DATASETS_DIR,
    )
    try:
        user_uuid = UUID(current_user["id"]) if current_user.get("id") else None
        result = service.explain_prediction(
            prediction_id  = prediction_id,
            feature_values = body.features,
            user_id        = user_uuid,
        )
        return {"success": True, "data": result}
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(exc)},
        )
    except UnsupportedModelError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": str(exc),
                "supported_algorithms": list(exc.supported_types),
            },
        )
    except ExplanationValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"success": False, "message": str(exc), "reasons": exc.reasons},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"success": False, "message": str(exc)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"Explanation error: {str(exc)}"},
        )


@router.get("/{prediction_id}")
def get_explanation_api(
    prediction_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Retrieve the latest persisted SHAP explanation for a prediction."""
    service = ExplainabilityService(
        db,
        base_dir=settings.MODEL_DIR,
        datasets_dir=settings.DATASETS_DIR,
    )
    try:
        record = service.get_latest_for_prediction(prediction_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": f"No explanation found for prediction '{prediction_id}'.",
                },
            )
        return {
            "success": True,
            "data": {
                "id":                          str(record.id),
                "prediction_id":               str(record.prediction_id),
                "model_id":                    str(record.model_id) if record.model_id else None,
                "model_version":               record.model_version,
                "algorithm":                   record.algorithm,
                "base_value":                  record.base_value,
                "feature_names":               record.feature_names,
                "shap_values":                 record.shap_values,
                "feature_importance":          record.feature_importance,
                "top_positive_contributors":   record.top_positive_contributors,
                "top_negative_contributors":   record.top_negative_contributors,
                "prediction_label":            record.prediction_label,
                "confidence":                  record.confidence,
                "warnings":                    record.warnings,
                "explained_at":                record.explained_at.isoformat() if record.explained_at else None,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(exc)},
        )
