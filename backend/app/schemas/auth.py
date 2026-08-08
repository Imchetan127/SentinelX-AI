from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str
    username: str
    role: str
    user_id: str


class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    is_active: bool
    last_login: Optional[str]

    model_config = ConfigDict(from_attributes=True)
