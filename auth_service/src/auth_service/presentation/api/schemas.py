import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from auth_service.domain.user import Role


class HealthResponse(BaseModel):
    status: str


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)

    model_config = ConfigDict(extra="forbid")


class LoginRequest(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(extra="forbid")


class RefreshRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class LogoutRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: Role
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
