# Wallet Platform

## Description

`wallet_platform` is a workspace for backend services built around a wallet domain.

Each service is isolated in its own directory and owns its own:
- source code
- tests
- Docker setup
- dependency configuration
- service-level README

At the current stage the platform contains:
- `wallet_service` for wallet balances, wallet operations, and event publishing
- `notification_service` for consuming wallet events and storing internal notifications

The platform already demonstrates an event-driven flow:
- `wallet_service` writes wallet operation events to a transactional outbox
- an outbox processor publishes events to Redpanda via FastStream
- `notification_service` consumes `wallet.transaction.created`
- the consumed event is persisted as a notification in its own database

## Structure

```text
wallet_platform/
├── README.md
├── docker-compose.yml
├── notification_service/
│   ├── README.md
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── src/
│   └── tests/
├── wallet_service/
│   ├── README.md
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── src/
│   └── tests/
└── ...
```

## Development approach

- keep services isolated
- use a simplified clean architecture
- avoid unnecessary enterprise complexity
- keep each step mergeable and runnable

## Local integration run

Start the shared local platform environment:

```bash
cd wallet_platform
docker compose up -d --build
```

This starts:
- `wallet_service` on `http://localhost:8000`
- `notification_service` on `http://localhost:8001`
- Redpanda on `localhost:19092`
- two isolated PostgreSQL databases for the services
