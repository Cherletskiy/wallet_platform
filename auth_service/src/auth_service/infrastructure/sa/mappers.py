from auth_service.domain.session import RefreshSession
from auth_service.domain.user import Role, User
from auth_service.infrastructure.sa.models import RefreshSessionModel, UserModel


def map_user(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        role=Role(model.role),
        is_active=model.is_active,
        is_email_verified=model.is_email_verified,
        created_at=model.created_at,
    )


def map_refresh_session(model: RefreshSessionModel) -> RefreshSession:
    return RefreshSession(
        id=model.id,
        user_id=model.user_id,
        family_id=model.family_id,
        created_at=model.created_at,
        expires_at=model.expires_at,
        revoked_at=model.revoked_at,
        replaced_by_session_id=model.replaced_by_session_id,
    )
