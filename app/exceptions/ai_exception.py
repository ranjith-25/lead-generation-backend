from typing import Any, Optional, Tuple

import httpx
from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode


class AIException(AppException):
    """Base exception for AI service related errors."""

    def __init__(
        self,
        message: str = "AI service error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = ErrorCode.AI_SERVICE_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=details,
        )


class AIConnectException(AIException):
    """Raised when unable to connect to the AI server (e.g., AI service is down, wrong host/port)."""

    def __init__(
        self,
        message: str = "Unable to connect to the AI server",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.AI_CONNECT_ERROR,
            details=details,
        )


class AIConnectTimeoutException(AIException):
    """Raised when connection to AI server times out (server didn't accept the connection)."""

    def __init__(
        self,
        message: str = "Connection to AI service timed out",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_code=ErrorCode.AI_CONNECT_TIMEOUT,
            details=details,
        )


class AIReadTimeoutException(AIException):
    """Raised when server took too long to respond (AI model is still processing)."""

    def __init__(
        self,
        message: str = "AI service read response timed out",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_code=ErrorCode.AI_READ_TIMEOUT,
            details=details,
        )


class AIWriteTimeoutException(AIException):
    """Raised when request payload upload to AI service times out."""

    def __init__(
        self,
        message: str = "Request upload to AI service timed out",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_code=ErrorCode.AI_WRITE_TIMEOUT,
            details=details,
        )


class AIPoolTimeoutException(AIException):
    """Raised when no connection is available in pool due to high traffic."""

    def __init__(
        self,
        message: str = "No connection available in pool for AI service",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.AI_POOL_TIMEOUT,
            details=details,
        )


class AITimeoutException(AIException):
    """Base exception for all timeout-related issues with AI service."""

    def __init__(
        self,
        message: str = "AI service operation timed out",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_code=ErrorCode.AI_TIMEOUT_ERROR,
            details=details,
        )


class AIHTTPStatusException(AIException):
    """Raised when AI service response status is 4xx or 5xx after raise_for_status()."""

    def __init__(
        self,
        message: str = "AI service returned an HTTP error status",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=ErrorCode.AI_HTTP_STATUS_ERROR,
            details=details,
        )


class AINetworkException(AIException):
    """Raised on network-level problems (connection reset, network unavailable)."""

    def __init__(
        self,
        message: str = "Network-level error occurred while contacting AI service",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=ErrorCode.AI_NETWORK_ERROR,
            details=details,
        )


class AIRemoteProtocolException(AIException):
    """Raised on invalid HTTP response from AI server (malformed response)."""

    def __init__(
        self,
        message: str = "Invalid HTTP response from AI server",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=ErrorCode.AI_REMOTE_PROTOCOL_ERROR,
            details=details,
        )


class AITooManyRedirectsException(AIException):
    """Raised when redirect loop is encountered (misconfigured API endpoint)."""

    def __init__(
        self,
        message: str = "Too many redirects encountered while connecting to AI service",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=ErrorCode.AI_TOO_MANY_REDIRECTS,
            details=details,
        )


class AIRequestException(AIException):
    """Base exception for request/network errors (DNS failures, SSL issues, connection errors)."""

    def __init__(
        self,
        message: str = "Request error occurred while contacting AI service",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=ErrorCode.AI_REQUEST_ERROR,
            details=details,
        )


class AIValueError(AIException):
    """Raised on invalid JSON or bad input processing (calling .json() on invalid JSON)."""

    def __init__(
        self,
        message: str = "Invalid JSON or bad input processing",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.AI_INVALID_RESPONSE_FORMAT,
            details=details,
        )


def get_ai_message(exc: Exception) -> Tuple[str, str, int]:
    """
    Maps httpx and processing exceptions to a tuple of (message, error_code, status_code).

    Supported exceptions:
    - httpx.ConnectError
    - httpx.ConnectTimeout
    - httpx.ReadTimeout
    - httpx.WriteTimeout
    - httpx.PoolTimeout
    - httpx.TimeoutException
    - httpx.HTTPStatusError
    - httpx.RequestError
    - httpx.NetworkError
    - httpx.RemoteProtocolError
    - httpx.TooManyRedirects
    - ValueError
    """
    if isinstance(exc, httpx.ConnectTimeout):
        return (
            "Connection to AI service timed out",
            ErrorCode.AI_CONNECT_TIMEOUT,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.ReadTimeout):
        return (
            "AI service took too long to respond",
            ErrorCode.AI_READ_TIMEOUT,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.WriteTimeout):
        return (
            "Request upload to AI service timed out",
            ErrorCode.AI_WRITE_TIMEOUT,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.PoolTimeout):
        return (
            "No connection available in pool for AI service",
            ErrorCode.AI_POOL_TIMEOUT,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, httpx.TimeoutException):
        return (
            "AI service request operation timed out",
            ErrorCode.AI_TIMEOUT_ERROR,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.ConnectError):
        return (
            "Unable to connect to the AI server",
            ErrorCode.AI_CONNECT_ERROR,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, httpx.NetworkError):
        return (
            "Network-level problem occurred while contacting AI service",
            ErrorCode.AI_NETWORK_ERROR,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, httpx.RemoteProtocolError):
        return (
            "Invalid HTTP response from AI server",
            ErrorCode.AI_REMOTE_PROTOCOL_ERROR,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, httpx.TooManyRedirects):
        return (
            "Too many redirects encountered while connecting to AI service",
            ErrorCode.AI_TOO_MANY_REDIRECTS,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = (
            exc.response.status_code
            if hasattr(exc, "response") and exc.response is not None
            else status.HTTP_502_BAD_GATEWAY
        )
        return (
            f"AI Service is Offline.",
            ErrorCode.AI_HTTP_STATUS_ERROR,
            status_code,
        )

    if isinstance(exc, httpx.RequestError):
        return (
            "Request error occurred while contacting AI service",
            ErrorCode.AI_REQUEST_ERROR,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, ValueError):
        return (
            "Invalid JSON or bad input processing",
            ErrorCode.AI_INVALID_RESPONSE_FORMAT,
            status.HTTP_400_BAD_REQUEST,
        )

    return (
        "Unknown AI service error",
        ErrorCode.AI_SERVICE_ERROR,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def handle_ai_exception(exc: Exception) -> AIException:
    """
    Translates an incoming httpx or ValueError exception into an AIException instance.
    """
    print(type(exc))
    print(repr(exc))
    message, error_code, status_code = get_ai_message(exc)
    return AIException(
        message=message,
        status_code=status_code,
        error_code=error_code,
        details=str(exc) if str(exc) else None,
    )
