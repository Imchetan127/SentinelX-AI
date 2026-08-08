from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AnalysisCreate(BaseModel):
    attack_id: UUID
    model_id: UUID
    prediction: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str = Field(min_length=1)
    recommendation: Optional[str] = None
    processing_time_ms: Optional[int] = None


class AnalysisOut(BaseModel):
    id: UUID
    attack_id: UUID
    model_id: UUID
    prediction: str
    confidence: float
    severity: str
    recommendation: Optional[str]
    processing_time_ms: Optional[int]
    created_at: str

    model_config = ConfigDict(from_attributes=True)
