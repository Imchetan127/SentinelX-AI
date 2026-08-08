from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ReportCreate(BaseModel):
    incident_id: UUID
    generated_by: Optional[UUID] = None
    report_type: str = Field(min_length=1, max_length=128)
    file_path: str = Field(min_length=1, max_length=512)


class ReportOut(BaseModel):
    id: UUID
    incident_id: UUID
    generated_by: Optional[UUID]
    report_type: str
    file_path: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)
