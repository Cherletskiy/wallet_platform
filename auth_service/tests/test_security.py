import uuid

from auth_service.application.common.security import JWTService, PasswordHasher
from auth_service.config import config
from auth_service.domain.user import User


def test_password_hasher_roundtrip() -> None:
    hasher = PasswordHasher()
    password_hash = hasher.hash_password("Password123")

    assert hasher.verify_password("Password123", password_hash) is True
    assert hasher.verify_password("wrong-password", password_hash) is False


def test_jwt_service_creates_and_decodes_tokens() -> None:
    jwt_service = JWTService(config)
    user = User(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        email="user@example.com",
        password_hash="hash",
    )

    access_token = jwt_service.create_access_token(user)
    refresh_token = jwt_service.create_refresh_token(user.id, uuid.uuid4())

    access_payload = jwt_service.decode_token(access_token, expected_type="access")
    refresh_payload = jwt_service.decode_token(refresh_token, expected_type="refresh")

    assert access_payload["sub"] == str(user.id)
    assert access_payload["email"] == user.email
    assert refresh_payload["sub"] == str(user.id)
    assert refresh_payload["type"] == "refresh"
