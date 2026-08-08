from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AttackCreate(BaseModel):
    attack_type: str = Field(min_length=1, max_length=128)
    payload: str
    target: Optional[str] = None
    severity: Optional[str] = "medium"
    status: Optional[str] = "open"
    source_ip: Optional[str] = None


class AttackOut(BaseModel):
    id: str
    user_id: str
    attack_type: str
    payload: str
    target: Optional[str]
    severity: str
    status: str
    source_ip: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)
