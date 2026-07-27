import base64
import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from auth_service.config import Config
from auth_service.domain.user import User

PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 600_000


class PasswordHasher:
    def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            password.encode(),
            salt,
            PBKDF2_ITERATIONS,
        )
        salt_b64 = base64.b64encode(salt).decode()
        digest_b64 = base64.b64encode(digest).decode()
        return f"pbkdf2_{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt_b64}${digest_b64}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        algorithm, iterations, salt_b64, expected_hash = password_hash.split("$", 3)
        if algorithm != f"pbkdf2_{PBKDF2_ALGORITHM}":
            return False
        salt = base64.b64decode(salt_b64.encode())
        digest = hashlib.pbkdf2_hmac(
            PBKDF2_ALGORITHM,
            password.encode(),
            salt,
            int(iterations),
        )
        actual_hash = base64.b64encode(digest).decode()
        return hmac.compare_digest(actual_hash, expected_hash)


class JWTService:
    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg

    def create_access_token(self, user: User) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "roles": [user.role.value],
            "email_verified": user.is_email_verified,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(
                (
                    now + timedelta(minutes=self._cfg.access_token_expire_minutes)
                ).timestamp()
            ),
        }
        return jwt.encode(payload, self._cfg.jwt_secret_key, algorithm="HS256")

    def create_refresh_token(self, user_id: uuid.UUID, session_id: uuid.UUID) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "jti": str(session_id),
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(
                (now + timedelta(days=self._cfg.refresh_token_expire_days)).timestamp()
            ),
        }
        return jwt.encode(payload, self._cfg.jwt_secret_key, algorithm="HS256")

    def decode_token(self, token: str, *, expected_type: str) -> dict[str, Any]:
        payload = jwt.decode(token, self._cfg.jwt_secret_key, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise jwt.InvalidTokenError("Invalid token type")
        return payload

    def refresh_session_expires_at(self) -> datetime:
        return datetime.now(UTC) + timedelta(days=self._cfg.refresh_token_expire_days)
