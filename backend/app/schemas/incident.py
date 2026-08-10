from datetime import datetime
from typing import Optional, Union
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
    analysis_result_id: Optional[UUID] = None
    assigned_user_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    opened_at: Optional[Union[datetime, str]] = None
    closed_at: Optional[Union[datetime, str]] = None
    created_at: Optional[Union[datetime, str]] = None

    model_config = ConfigDict(from_attributes=True)
