import jwt
import pytest

from bff_service.config import config

pytestmark = pytest.mark.asyncio


def make_access_token() -> str:
    return jwt.encode(
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


async def test_health(client) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_auth_login_is_proxied(client, downstream_gateway) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "Password123"},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert downstream_gateway.last_call == {
        "method": "POST",
        "path": "/api/v1/auth/login",
        "body": {"email": "user@example.com", "password": "Password123"},
        "headers": None,
    }


async def test_wallet_get_forwards_identity_headers(client, downstream_gateway) -> None:
    token = make_access_token()

    response = await client.get(
        "/api/v1/wallets/11111111-1111-1111-1111-111111111111",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"balance_rub": 100.0}
    assert downstream_gateway.last_call is not None
    assert downstream_gateway.last_call["headers"] == {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Roles": "user",
        "X-User-Email-Verified": "true",
    }


async def test_wallet_operation_requires_valid_token(client) -> None:
    response = await client.post(
        "/api/v1/wallets/11111111-1111-1111-1111-111111111111/operation",
        headers={"Authorization": "Bearer not-a-jwt"},
        json={"amount": "10.00", "operation_type": "DEPOSIT"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid access token"}
