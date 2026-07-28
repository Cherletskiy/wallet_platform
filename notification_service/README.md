# Notification Service

## Description

`notification_service` consumes wallet transaction events and stores internal notifications.

At the current stage the service:
- consumes `wallet.transaction.created`
- stores notifications in PostgreSQL
- exposes a small HTTP API for health and user-scoped notification listing
- uses FastStream with a Kafka-compatible broker
- is designed as a separate microservice inside `wallet_platform`

## Event flow

1. `wallet_service` publishes `wallet.transaction.created`
2. `notification_service` consumes the event from Redpanda
3. the consumer validates and processes the message idempotently
4. a notification row is stored in the service database

Notifications are stored with both `user_id` and `wallet_id`, so the service
can return all notifications of the current user or a subset for one wallet.

The notification message currently depends on the wallet operation type:
- `DEPOSIT` -> `Deposit received: ...`
- `WITHDRAWAL` -> `Withdrawal completed: ...`

## Local development

```bash
cd wallet_platform/notification_service
uv sync --group dev
docker compose up -d
uv run python -m notification_service --reload
```

## Shared platform run

To run the service together with `wallet_service` and a shared broker:

```bash
cd wallet_platform
docker compose up -d --build
```

## Quality checks

```bash
uv run ruff check src tests
uv run mypy src/notification_service
uv run pytest
```

## API

- `GET /api/v1/health`
- `GET /api/v1/notifications`

Swagger UI is available at `http://localhost:8001/docs`.

`GET /api/v1/notifications` requires trusted identity headers and supports:
- `limit`
- optional `wallet_id`
