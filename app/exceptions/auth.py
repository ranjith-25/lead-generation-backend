from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class InvalidCredentialsException(AppException):

    def __init__(self):
        super().__init__(
            message="Invalid username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.INVALID_CREDENTIALS,
        )


class SessionExpiredException(AppException):

    def __init__(self):
        super().__init__(
            message="Session expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.SESSION_EXPIRED,
        )


class TokenExpiredException(AppException):

    def __init__(self):
        super().__init__(
            message="Token expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.TOKEN_EXPIRED,
        )

class PermissionRequired(AppException):
    def __init__(self):
        super().__init__(
            message="No enough permissions",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.NOT_ALLOWED
        )