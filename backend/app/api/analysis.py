from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.schemas.analysis import AnalysisCreate, AnalysisOut
from app.services.analysis_service import AnalysisService

router = APIRouter(
    prefix="/analysis",
    tags=["AI Analysis"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=AnalysisOut)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    analysis = service.create_analysis(
        attack_id=payload.attack_id,
        model_id=payload.model_id,
        prediction=payload.prediction,
        confidence=payload.confidence,
        severity=payload.severity,
        recommendation=payload.recommendation,
        processing_time_ms=payload.processing_time_ms,
    )
    return analysis


@router.get("/", response_model=List[AnalysisOut])
def list_analysis(db: Session = Depends(get_db)):
    service = AnalysisService(db)
    return service.list_analysis()


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: UUID, db: Session = Depends(get_db)):
    service = AnalysisService(db)
    analysis = service.get_analysis(analysis_id)
    if not analysis or analysis.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis result not found")
    return analysis
