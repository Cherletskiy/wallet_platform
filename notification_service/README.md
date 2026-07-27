# Notification Service

## Description

`notification_service` consumes wallet transaction events and stores internal notifications.

At the current stage the service:
- consumes `wallet.transaction.created`
- stores notifications in PostgreSQL
- exposes a small HTTP API for health and notification listing

## Local development

```bash
cd wallet_platform/notification_service
uv sync --group dev
docker compose up -d
uv run python -m notification_service --reload
```

## Quality checks

```bash
uv run ruff check src tests
uv run mypy src/notification_service
uv run pytest
```
