from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_admin, get_current_user
from app.database.session import get_db
from app.schemas.model import ModelCreate, ModelOut
from app.services.model_service import ModelService

router = APIRouter(
    prefix="/models",
    tags=["Trained Models"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ModelOut, dependencies=[Depends(get_current_admin)])
def create_model(payload: ModelCreate, db: Session = Depends(get_db)):
    service = ModelService(db)
    model = service.create_model(
        name=payload.name,
        algorithm=payload.algorithm,
        dataset=payload.dataset,
        version=payload.version,
        accuracy=payload.accuracy,
        precision=payload.precision,
        recall=payload.recall,
        f1_score=payload.f1_score,
        file_path=payload.file_path,
        trained_at=payload.trained_at,
        is_active=payload.is_active,
    )
    return model


@router.get("/", response_model=List[ModelOut])
def list_models(db: Session = Depends(get_db)):
    service = ModelService(db)
    return service.list_models()
