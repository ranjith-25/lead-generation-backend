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


class UserDeletedException(AppException):
    """A JWT minted before the account was soft-deleted is still cryptographically valid and
    its session row may still be live, so neither of those checks catches it - this does."""

    def __init__(self):
        super().__init__(
            message="This account has been deleted",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.USER_DELETED,
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
    
class WeakPasswordException(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.WEAK_PASSWORD,
        )
        
class NoUserException(AppException):
    def __init__(self, message: str):
            super().__init__(
                message=message,
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.USER_NOT_FOUND,
            )