# Wallet Service

## Description

`wallet_service` is an isolated service inside `wallet_platform`.
It manages wallet balances, applies `DEPOSIT` and `WITHDRAWAL` operations,
stores money in cents, and exposes balances in rubles through HTTP API.

The service follows a simplified clean architecture approach:
- `presentation` contains FastAPI routers and schemas
- `application` contains interactors and ports
- `domain` contains business entities and domain errors
- `infrastructure` contains SQLAlchemy, migrations, logging, and DI adapters

## Service structure

```text
wallet_platform/
└── wallet_service/
    ├── src/
    │   └── wallet_service/
    │       ├── application/
    │       │   ├── commands/
    │       │   ├── queries/
    │       │   └── unit_of_work.py
    │       ├── domain/
    │       ├── infrastructure/
    │       │   ├── logging.py
    │       │   └── sa/
    │       │           ├── alembic/
    │       │           ├── repositories/
    │       │           ├── models.py
    │       │           ├── session.py
    │       │           └── unit_of_work.py
    │       ├── presentation/
    │       │   └── api/
    │       ├── config.py
    │       ├── ioc.py
    │       ├── __init__.py
    │       └── __main__.py
    ├── tests/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── local.env
    ├── pyproject.toml
    └── uv.lock
```

## Requirements

- Python 3.12+
- `uv`
- Docker and Docker Compose

## Local development

1. Enter the service directory:
```bash
cd wallet_platform/wallet_service
```

2. Create the virtual environment and install dependencies:
```bash
uv sync --group dev
```

3. Start local infrastructure:
```bash
docker compose up -d
```

4. Run the service locally:
```bash
uv run python -m wallet_service --reload
```

## Quality checks

```bash
uv run ruff check src tests
uv run mypy src/wallet_service
```

## API

- `GET /api/v1/wallets/{wallet_id}` returns the current balance in rubles
- `POST /api/v1/wallets/{wallet_id}/operation` applies `DEPOSIT` or `WITHDRAWAL`

Swagger UI is available at `http://localhost:8000/docs`.

## Notes

- Concurrency is handled with `SELECT FOR UPDATE`
- The application uses `dishka` for dependency injection
- Alembic migrations live in `infrastructure/sa/alembic` and run on startup
