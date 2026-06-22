# Wallet API

## Description

Wallet API is a FastAPI service for wallet balance management backed by PostgreSQL. It supports deposit and withdrawal operations, handles concurrent updates with `SELECT FOR UPDATE`, stores money in cents for accuracy, and exposes balances in rubles through the API.

This first upgrade step introduces a modern Python project setup with `uv`, `pyproject.toml`, `ruff`, and `mypy` while preserving the current application behavior.

## Requirements

- Python 3.12+
- `uv`
- Docker and Docker Compose
- PostgreSQL 15+

## Project structure

```
wallet_platform/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # API endpoints
│   │   │   ├── schemas.py       # Pydantic schemas
│   │   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # Database initialization
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   ├── logging_config.py    # Logging configuration
│   │   ├── migrations.py        # Alembic migration runner
│   ├── models/
│   │   ├── __init__.py
│   │   ├── wallet.py            # SQLAlchemy models (Wallet, Operation)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── wallet_repository.py # Database access logic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── wallet_service.py    # Business logic
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Test fixtures
│   │   ├── test_concurrency.py  # Concurrency tests
│   │   ├── test_repository.py   # Repository tests
│   │   ├── test_routes.py       # Endpoint tests
│   │   ├── test_services.py     # Service tests
├── alembic/
│   ├── versions/                # Migration files
│   ├── env.py                  # Alembic configuration
├── .coveragerc                 # pytest-cov configuration
├── .env                        # Environment variables
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker Compose for the app, databases, and pgAdmin
├── Dockerfile                  # Docker image for the application
├── pyproject.toml              # Project metadata, dependencies, pytest, ruff
└── README.md
```

## Local development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd wallet_platform
   ```

2. Create an environment file:
   ```bash
   cp _env .env
   ```

3. Install dependencies:
   ```bash
   uv sync --group dev
   ```

4. Start the local stack:
   ```bash
   docker compose up -d
   ```

5. Run the application locally:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

6. Run tests:
   ```bash
   uv run pytest app/tests -v --cov=app --cov-report=term
   ```

7. Run lint:
   ```bash
   uv run ruff check .
   ```

8. Run type checks:
   ```bash
   uv run mypy app
   ```

## Docker

```bash
docker compose up -d --build
```

This starts:
- PostgreSQL for the app on `5431`
- PostgreSQL for tests on `5433`
- pgAdmin on `8080`
- FastAPI on `8000`

## Create a wallet

The current API does not expose wallet creation yet, so create a wallet manually.

Using pgAdmin:
- Open `http://localhost:8080`
- Sign in with `admin@admin.com` / `admin`
- Connect to `db` with user `postgres` and password `postgres`
- Execute:
  ```sql
  INSERT INTO wallets (id, balance_cent) VALUES (gen_random_uuid(), 0);
  ```

Using `psql`:
```bash
docker compose exec db psql -U postgres -d postgres
INSERT INTO wallets (id, balance_cent) VALUES (gen_random_uuid(), 0);
```

## API endpoints

- `GET /api/v1/wallets/{wallet_id}`
  Returns wallet balance in rubles.

- `POST /api/v1/wallets/{wallet_id}/operation`
  Performs a `DEPOSIT` or `WITHDRAWAL` and returns the updated balance.

Swagger UI is available at `http://localhost:8000/docs`.

## Database

- Main database: PostgreSQL on `5431`
- Test database: PostgreSQL on `5433`
- Migrations: Alembic in [alembic](./alembic)

## Tooling

- Dependency management: `uv`
- Linting: `ruff`
- Type checking: `mypy`
- Testing: `pytest`

## Notes

- Concurrency is handled with `SELECT FOR UPDATE` in the wallet repository.
- Monetary values are stored in cents and returned in rubles.
- CI is not configured yet.
