import uuid

import jwt
import pytest

from bff_service.application.common.identity import (
    IdentityService,
    build_identity_headers,
)
from bff_service.config import config


def test_identity_service_decodes_access_token() -> None:
    token = jwt.encode(
        {
            "sub": "11111111-1111-1111-1111-111111111111",
            "email": "user@example.com",
            "roles": ["user"],
            "email_verified": True,
            "type": "access",
        },
        config.jwt_secret_key,
        algorithm="HS256",
    )

    service = IdentityService(config)
    user = service.get_current_user(token)

    assert user.user_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
    assert user.email == "user@example.com"
    assert user.roles == ["user"]
    assert user.email_verified is True


def test_identity_headers_mapping() -> None:
    service = IdentityService(config)
    token = jwt.encode(
        {
            "sub": "11111111-1111-1111-1111-111111111111",
            "email": "user@example.com",
            "roles": ["user", "admin"],
            "email_verified": False,
            "type": "access",
        },
        config.jwt_secret_key,
        algorithm="HS256",
    )

    user = service.get_current_user(token)
    headers = build_identity_headers(user)

    assert headers["X-User-Id"] == "11111111-1111-1111-1111-111111111111"
    assert headers["X-User-Roles"] == "user,admin"
    assert headers["X-User-Email-Verified"] == "false"


def test_identity_service_rejects_wrong_token_type() -> None:
    token = jwt.encode(
        {
            "sub": "11111111-1111-1111-1111-111111111111",
            "type": "refresh",
        },
        config.jwt_secret_key,
        algorithm="HS256",
    )

    service = IdentityService(config)

    with pytest.raises(jwt.InvalidTokenError):
        service.get_current_user(token)
