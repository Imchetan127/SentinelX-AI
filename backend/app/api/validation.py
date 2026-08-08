from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any, List, Optional

from app.database.session import get_db
from app.core.security import get_current_user, get_current_admin
from app.ml_engine.validation.service import ValidationService

router = APIRouter(
    prefix="/validation",
    tags=["AI Validation & Benchmarking"],
)


@router.post("/validate/{model_id}")
def validate_model_api(
    model_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Validate a specific registered model by its model_id string or UUID (Admin only)."""
    service = ValidationService(db)
    try:
        user_uuid = UUID(current_admin["id"]) if current_admin.get("id") else None
        result = service.validate_model(model_id, user_id=user_uuid)
        return {
            "success": True,
            "message": f"Validation completed for model '{model_id}'.",
            "data": result,
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(e)}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"Validation error: {str(e)}"}
        )


@router.post("/benchmark")
def run_benchmark_api(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Run full validation benchmark across all eligible registered models (Admin only)."""
    service = ValidationService(db)
    try:
        user_uuid = UUID(current_admin["id"]) if current_admin.get("id") else None
        benchmark_results = service.run_benchmark(user_id=user_uuid)
        return {
            "success": True,
            "message": "Benchmark run completed successfully.",
            "data": benchmark_results,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"Benchmark error: {str(e)}"}
        )


@router.get("/results")
def list_validation_results_api(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """List recent model validation results (Authenticated users)."""
    service = ValidationService(db)
    try:
        records = service.list_results(limit=limit, offset=offset)
        items = [
            {
                "id": str(r.id),
                "model_id": str(r.model_id) if r.model_id else None,
                "validator_version": r.validator_version,
                "dataset_version": r.dataset_version,
                "pipeline_version": r.pipeline_version,
                "quality_gate_result": r.quality_gate_result,
                "quality_gate_reasons": r.quality_gate_reasons,
                "validated_at": r.validated_at.isoformat() if r.validated_at else None,
            }
            for r in records
        ]
        return {"success": True, "count": len(items), "data": items}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.get("/results/{model_id}")
def get_latest_model_validation_api(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the latest validation result for a specific model (Authenticated users)."""
    service = ValidationService(db)
    try:
        record = service.get_latest_for_model(model_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"success": False, "message": f"No validation result found for model '{model_id}'."}
            )
        return {
            "success": True,
            "data": {
                "id": str(record.id),
                "model_id": str(record.model_id) if record.model_id else None,
                "validator_version": record.validator_version,
                "dataset_version": record.dataset_version,
                "pipeline_version": record.pipeline_version,
                "metrics": record.metrics,
                "cv_metrics": record.cv_metrics,
                "threshold_results": record.threshold_results,
                "quality_gate_result": record.quality_gate_result,
                "quality_gate_reasons": record.quality_gate_reasons,
                "warnings": record.warnings,
                "validated_at": record.validated_at.isoformat() if record.validated_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.get("/report/{result_id}")
def get_validation_report_api(
    result_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get full structured validation report by result_id UUID (Authenticated users)."""
    service = ValidationService(db)
    try:
        record = service.get_result_by_id(result_id)
        if not record or not record.report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"success": False, "message": f"Validation report '{result_id}' not found."}
            )
        return {"success": True, "data": record.report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )
