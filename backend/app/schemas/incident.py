from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class IncidentCreate(BaseModel):
    analysis_result_id: UUID
    assigned_user_id: Optional[UUID] = None
    title: str = Field(min_length=1, max_length=256)
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "OPEN"


class IncidentOut(BaseModel):
    id: UUID
    analysis_result_id: UUID
    assigned_user_id: Optional[UUID]
    title: str
    description: Optional[str]
    priority: str
    status: str
    opened_at: str
    closed_at: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)
