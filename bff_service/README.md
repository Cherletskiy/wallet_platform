# BFF Service

`bff_service` is the client-facing entrypoint for `wallet_platform`.
It validates `access_token` locally, converts JWT claims into trusted
`X-User-*` headers, and proxies requests to internal services.

## Current responsibilities

- proxy auth requests to `auth_service`
- validate access tokens at the platform edge
- forward trusted identity context to downstream services
- proxy wallet operations to `wallet_service`
- proxy user notifications to `notification_service`

## Exposed API

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/wallets`
- `POST /api/v1/wallets`
- `GET /api/v1/wallets/{wallet_id}`
- `POST /api/v1/wallets/{wallet_id}/operation`
- `GET /api/v1/notifications`

Swagger UI is available at `http://localhost:8003/docs`.
