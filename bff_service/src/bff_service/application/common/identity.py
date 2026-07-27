import uuid
from typing import Any

import jwt

from bff_service.config import Config
from bff_service.domain.identity import UserContext


class IdentityService:
    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg

    def get_current_user(self, token: str) -> UserContext:
        payload = self._decode_access_token(token)
        return UserContext(
            user_id=uuid.UUID(payload["sub"]),
            email=str(payload["email"]),
            roles=[str(role) for role in payload.get("roles", [])],
            email_verified=bool(payload.get("email_verified", False)),
        )

    def _decode_access_token(self, token: str) -> dict[str, Any]:
        payload = jwt.decode(token, self._cfg.jwt_secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError("Invalid token type")
        return payload


def build_identity_headers(user: UserContext) -> dict[str, str]:
    return {
        "X-User-Id": str(user.user_id),
        "X-User-Roles": ",".join(user.roles),
        "X-User-Email-Verified": str(user.email_verified).lower(),
    }
