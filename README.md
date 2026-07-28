# Wallet Platform

## Overview

`wallet_platform` is a small event-driven backend platform built as a set of isolated services around wallet operations, authentication, notifications, and a single client-facing entrypoint.

At the current stage the platform includes:
- `auth_service` for registration, login, JWT issuing, refresh rotation, logout, and current user lookup
- `wallet_service` for wallet creation, wallet listing, balance reads, wallet operations, and transactional outbox publishing
- `notification_service` for consuming wallet events and storing user-scoped internal notifications
- `bff_service` as the public platform entrypoint for clients
- `Redpanda` as a Kafka-compatible local broker
- isolated PostgreSQL databases for each stateful service

The platform follows a simplified microservice style:
- each service has its own source code, tests, dependencies, Docker setup, and README
- internal services are private in the shared local environment
- external client traffic goes through `bff_service`

## Services

### `bff_service`

Client-facing entrypoint.

Responsibilities:
- validate `access_token` at the platform edge
- proxy auth requests to `auth_service`
- proxy wallet requests to `wallet_service`
- proxy notification requests to `notification_service`
- convert JWT claims into trusted `X-User-*` headers for downstream services

Public docs:
- `http://localhost:8003/docs`

### `auth_service`

Authentication and session management.

Responsibilities:
- `email + password` registration and login
- issue short-lived JWT `access_token`
- issue database-backed `refresh_token`
- refresh rotation and logout
- return current user via `GET /api/v1/auth/me`

Internal service docs:
- not published externally in the shared platform setup

### `wallet_service`

Wallet domain service.

Responsibilities:
- create wallets for the current user
- list all wallets of the current user
- read a wallet balance
- apply `DEPOSIT` and `WITHDRAWAL`
- write `wallet.transaction.created` into a transactional outbox
- publish outbox events through FastStream to Redpanda

### `notification_service`

Notification consumer service.

Responsibilities:
- consume `wallet.transaction.created`
- persist notifications with `user_id` and `wallet_id`
- return user-scoped notifications

## Shared local environment

Run the whole platform:

```bash
cd wallet_platform
docker compose up -d --build
```

The shared setup exposes:
- `bff_service` on `http://localhost:8003`
- Redpanda Kafka API on `localhost:19092`
- Redpanda Pandaproxy on `localhost:18082`
- PostgreSQL ports for local inspection:
  - `wallet_db` -> `localhost:5431`
  - `notification_db` -> `localhost:5433`
  - `auth_db` -> `localhost:5434`

Important:
- only `bff_service` is intended to be called by the client
- `wallet_service`, `auth_service`, and `notification_service` stay inside the Docker network in the shared setup

## Public API Through BFF

These are the main client-facing endpoints exposed by `bff_service`:

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

### Wallets

- `GET /api/v1/wallets`
- `POST /api/v1/wallets`
- `GET /api/v1/wallets/{wallet_id}`
- `POST /api/v1/wallets/{wallet_id}/operation`

### Notifications

- `GET /api/v1/notifications`

Supported query params:
- `limit`
- optional `wallet_id`

### Health

- `GET /api/v1/health`

## User Flow

The main platform flow now looks like this:

1. A client registers through `POST /api/v1/auth/register`
2. The client logs in through `POST /api/v1/auth/login`
3. `auth_service` returns `access_token` and `refresh_token`
4. The client calls `bff_service` with `Authorization: Bearer <access_token>`
5. `bff_service` validates the JWT and forwards trusted identity headers to internal services
6. The client creates a wallet with `POST /api/v1/wallets`
7. The client reads all owned wallets with `GET /api/v1/wallets`
8. The client applies `DEPOSIT` or `WITHDRAWAL`
9. `wallet_service` writes `wallet.transaction.created` to its outbox in the same transaction
10. The outbox processor publishes the event to Redpanda
11. `notification_service` consumes the event and stores a user notification
12. The client reads notifications through `GET /api/v1/notifications`

## Service Interaction

### Request path

Normal synchronous request flow:

```text
Client
  -> BFF
  -> auth_service / wallet_service / notification_service
```

### Identity flow

Authentication and service trust work like this:

1. `auth_service` issues JWTs
2. `bff_service` validates `access_token`
3. `bff_service` extracts claims
4. `bff_service` sends trusted headers downstream:
   - `X-User-Id`
   - `X-User-Roles`
   - `X-User-Email-Verified`
5. internal services use this identity context for access control

### Event flow

Asynchronous flow:

```text
wallet_service
  -> transactional outbox
  -> outbox processor
  -> Redpanda
  -> notification_service
```

Current event:
- `wallet.transaction.created`

Current payload includes:
- `user_id`
- `wallet_id`
- `operation_type`
- `amount_cent`
- `balance_cent`

## Example Manual Flow

Register:

```bash
curl -X POST http://localhost:8003/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"Password123"}'
```

Login:

```bash
curl -X POST http://localhost:8003/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"Password123"}'
```

Create a wallet:

```bash
curl -X POST http://localhost:8003/api/v1/wallets \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

List wallets:

```bash
curl http://localhost:8003/api/v1/wallets \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Apply a deposit:

```bash
curl -X POST http://localhost:8003/api/v1/wallets/WALLET_ID/operation \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"amount":"100.00","operation_type":"DEPOSIT"}'
```

Read notifications:

```bash
curl "http://localhost:8003/api/v1/notifications?limit=50" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Per-Service Development

Each service is developed from its own directory.

Typical setup inside a service:

```bash
uv sync --group dev
docker compose up -d
uv run python -m <service_name> --reload
```

Service directories:
- `wallet_platform/auth_service`
- `wallet_platform/wallet_service`
- `wallet_platform/notification_service`
- `wallet_platform/bff_service`

## Quality Checks

You can run checks service-by-service from each service directory.

Recommended commands:

```bash
uv run pytest
uv run ruff check --fix --unsafe-fixes
uv run ruff format
uv run mypy .
```

Notes:
- some services also use narrower `mypy` targets such as `uv run mypy src/wallet_service`
- integration tests that rely on `testcontainers` require Docker
- for quick iteration, it is often convenient to run checks from the concrete service directory rather than from the platform root

## Repository Structure

```text
wallet_platform/
├── README.md
├── docker-compose.yml
├── auth_service/
│   ├── README.md
│   ├── Dockerfile
│   ├── local.env
│   ├── pyproject.toml
│   ├── src/
│   └── tests/
├── bff_service/
│   ├── README.md
│   ├── Dockerfile
│   ├── local.env
│   ├── pyproject.toml
│   ├── src/
│   └── tests/
├── notification_service/
│   ├── README.md
│   ├── Dockerfile
│   ├── local.env
│   ├── pyproject.toml
│   ├── src/
│   └── tests/
└── wallet_service/
    ├── README.md
    ├── Dockerfile
    ├── local.env
    ├── pyproject.toml
    ├── src/
    └── tests/
```
