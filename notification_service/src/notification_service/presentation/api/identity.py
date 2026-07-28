import uuid

from fastapi import Request

from notification_service.domain.exceptions import AuthorizationError
from notification_service.domain.identity import UserContext

USER_ID_HEADER = "X-User-Id"
USER_ROLES_HEADER = "X-User-Roles"
USER_EMAIL_VERIFIED_HEADER = "X-User-Email-Verified"


class HTTPIdentityProvider:
    def __init__(self, request: Request) -> None:
        self._request = request

    async def get_current_user(self) -> UserContext:
        raw_user_id = self._request.headers.get(USER_ID_HEADER)
        if raw_user_id is None:
            raise AuthorizationError("Missing trusted user id header")

        try:
            user_id = uuid.UUID(raw_user_id)
        except ValueError as exc:
            raise AuthorizationError("Invalid user id") from exc

        return UserContext(
            user_id=user_id,
            roles=self._parse_roles(),
            email_verified=self._is_email_verified(),
        )

    def _parse_roles(self) -> set[str]:
        raw_roles = self._request.headers.get(USER_ROLES_HEADER, "")
        return {role.strip().lower() for role in raw_roles.split(",") if role.strip()}

    def _is_email_verified(self) -> bool:
        raw_value = self._request.headers.get(USER_EMAIL_VERIFIED_HEADER, "")
        return raw_value.strip().lower() == "true"
