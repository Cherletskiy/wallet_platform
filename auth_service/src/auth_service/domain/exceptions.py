class AuthError(Exception):
    pass


class EmailAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InvalidRefreshTokenError(AuthError):
    pass


class UserNotFoundError(AuthError):
    pass
