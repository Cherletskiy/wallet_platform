from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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


class WalletOperationRequest(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    operation_type: str

    model_config = ConfigDict(extra="forbid")
