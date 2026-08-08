from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any, List

from app.database.session import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.enums import ModelStatus
from app.services.model_governance_service import ModelGovernanceService

router = APIRouter(
    prefix="/governance",
    tags=["Model Governance & Lifecycle"],
)


@router.get("/models")
def list_governed_models(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    # List all models indexed in the Model Registry
    gov_service = ModelGovernanceService(db)
    try:
        return gov_service._load_registry()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"Failed to retrieve model registry: {str(e)}"}
        )


@router.get("/models/{model_id}/card")
def get_model_card_api(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    gov_service = ModelGovernanceService(db)
    try:
        return gov_service.get_model_card(model_id)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.post("/models/{model_id}/promote")
def promote_model_api(
    model_id: UUID,
    target_status: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
) -> Dict[str, Any]:
    # Promote/archive/rollback are admin only
    gov_service = ModelGovernanceService(db)
    try:
        status_enum = ModelStatus[target_status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": f"Invalid lifecycle status parameter: '{target_status}'."}
        )

    try:
        user_uuid = UUID(current_admin["id"]) if current_admin.get("id") else None
        res = gov_service.promote_model(model_id, status_enum, user_uuid)
        return {"success": True, "message": f"Model promoted to {status_enum.value} successfully.", "model": res}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": str(e)}
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.post("/models/{model_id}/archive")
def archive_model_api(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
) -> Dict[str, Any]:
    gov_service = ModelGovernanceService(db)
    try:
        user_uuid = UUID(current_admin["id"]) if current_admin.get("id") else None
        res = gov_service.archive_model(model_id, user_uuid)
        return {"success": True, "message": "Model archived successfully.", "model": res}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": str(e)}
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.post("/rollback")
def rollback_model_api(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
) -> Dict[str, Any]:
    gov_service = ModelGovernanceService(db)
    try:
        user_uuid = UUID(current_admin["id"]) if current_admin.get("id") else None
        res = gov_service.rollback_model(user_uuid)
        return {"success": True, "message": "Model successfully rolled back to previous active version.", "model": res}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": str(e)}
        )


@router.get("/active")
def get_active_model_api(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    gov_service = ModelGovernanceService(db)
    try:
        return gov_service.get_active_model()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": str(e)}
        )
