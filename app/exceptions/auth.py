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

class InvalidResetTokenException(AppException):
    """Unknown, expired and already-used reset tokens all raise this same error on purpose —
    telling them apart would confirm to a stranger that a given token once existed."""

    def __init__(self):
        super().__init__(
            message="This password reset token is invalid or has expired",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVALID_RESET_TOKEN,
        )


class InvalidOtpException(AppException):
    """Unknown, expired and already-used OTPs all raise this same error on purpose."""

    def __init__(self):
        super().__init__(
            message="This OTP is invalid or has expired",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVALID_OTP,
        )


class EmailSendFailedException(AppException):
    def __init__(self):
        super().__init__(
            message="The verification email could not be sent. Please try again later",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.EMAIL_SEND_FAILED,
        )


class PermissionRequired(AppException):
    def __init__(self):
        super().__init__(
            message="No enough permissions",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=ErrorCode.NOT_ALLOWED
        )