from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    algorithm: str = Field(min_length=1, max_length=128)
    dataset: str = Field(min_length=1, max_length=256)
    version: str = Field(min_length=1, max_length=64)
    accuracy: float = Field(ge=0.0, le=1.0)
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    f1_score: float = Field(ge=0.0, le=1.0)
    file_path: str = Field(min_length=1, max_length=512)
    trained_at: datetime
    is_active: Optional[bool] = True


class ModelOut(BaseModel):
    id: UUID
    name: str
    algorithm: str
    dataset: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    file_path: str
    is_active: bool
    trained_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
