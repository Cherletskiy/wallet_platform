import uuid
from datetime import UTC, datetime

import pytest

from auth_service.domain.user import Role, User

pytestmark = pytest.mark.asyncio


async def test_health(client) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_register_route(client, mock_register_interactor, test_user) -> None:
    mock_register_interactor.execute.return_value = test_user

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": test_user.email, "password": "Password123"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == test_user.email


async def test_login_route(client, mock_login_interactor, issued_token_pair) -> None:
    mock_login_interactor.execute.return_value = issued_token_pair

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "Password123"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": issued_token_pair.access_token,
        "refresh_token": issued_token_pair.refresh_token,
        "token_type": "bearer",
    }


async def test_refresh_route(
    client, mock_refresh_interactor, issued_token_pair
) -> None:
    mock_refresh_interactor.execute.return_value = issued_token_pair

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "refresh-token"},
    )

    assert response.status_code == 200
    assert response.json()["refresh_token"] == issued_token_pair.refresh_token


async def test_logout_route(client, mock_logout_interactor) -> None:
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "refresh-token"},
    )

    assert response.status_code == 204
    mock_logout_interactor.execute.assert_awaited_once()


async def test_me_route(client, mock_me_interactor, jwt_service) -> None:
    user = User(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        email="user@example.com",
        password_hash="hash",
        role=Role.USER,
        created_at=datetime.now(UTC),
    )
    mock_me_interactor.execute.return_value = user
    access_token = jwt_service.create_access_token(user)

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)
    assert response.json()["email"] == user.email
