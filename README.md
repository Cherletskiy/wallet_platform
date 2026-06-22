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
- `wallet_service` for wallet balances and wallet operations

## Structure

```text
wallet_platform/
├── README.md
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
