from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class AttackCreate(BaseModel):
    attack_type: str = Field(min_length=1, max_length=128)
    payload: str
    target: Optional[str] = None
    severity: Optional[str] = "medium"
    status: Optional[str] = "open"
    source_ip: Optional[str] = None


class AttackOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    attack_type: str
    payload: str
    target: Optional[str] = None
    severity: str
    status: str
    source_ip: Optional[str] = None
    created_at: Any = None

    @field_validator("id", "user_id", mode="before")
    def convert_uuid_to_str(cls, v):
        return str(v) if v is not None else None

    @field_validator("created_at", mode="before")
    def convert_dt_to_str(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v) if v is not None else None

    model_config = ConfigDict(from_attributes=True)
