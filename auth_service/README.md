# Auth Service

`auth_service` manages user registration, login, JWT issuing, refresh rotation,
logout, and current user lookup for `wallet_platform`.

The service is intentionally focused on core authentication mechanics:
- `email + password` authentication
- short-lived `access_token`
- database-backed `refresh_token` rotation
- logout through refresh session revocation
- current user lookup with `GET /api/v1/auth/me`

## Architecture

`auth_service` follows the same service structure as the rest of the platform:
- `presentation` contains FastAPI routers and response models
- `application` contains interactors, DTOs, and security services
- `domain` contains users, refresh sessions, and domain exceptions
- `infrastructure` contains SQLAlchemy, Alembic, logging, and DI wiring

## Local development

1. Enter the service directory:
```bash
cd wallet_platform/auth_service
```

2. Install dependencies:
```bash
uv sync --group dev
```

3. Start local infrastructure:
```bash
docker compose up -d
```

4. Run the service locally:
```bash
uv run python -m auth_service --reload
```

## Quality checks

```bash
uv run ruff check src tests
uv run mypy .
uv run pytest
```

## API

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/health`

Swagger UI is available at `http://localhost:8002/docs`.

## Notes

- Passwords are hashed with `PBKDF2-HMAC-SHA256`
- Refresh sessions are stored in PostgreSQL
- Access tokens are stateless JWTs
- Refresh rotation revokes the previous refresh session
- The shared platform setup can be started from [`wallet_platform/docker-compose.yml`](/home/cherletskiy/Projects/UPGARDE/wallet_platform/docker-compose.yml:1)
