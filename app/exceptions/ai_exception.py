import logging
from typing import Any, Optional, Tuple

import httpx
from fastapi import status

from app.exceptions.custom import AppException
from app.exceptions.error_codes import ErrorCode

logger = logging.getLogger(__name__)

MAX_AI_ERROR_BODY_LENGTH = 2000

PASSTHROUGH_AI_STATUS_CODES = frozenset(
    {
        400,  # bad request
        409,  # conflict
        413,  # payload too large
        415,  # unsupported media type
        422,  # unprocessable content
    }
)


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


def read_ai_error_body(response: Optional[httpx.Response]) -> Any:
    """The AI service's error payload, parsed when it is JSON and truncated when it is not.

    `str(httpx.HTTPStatusError)` only ever contains the status line and the URL, so the
    body has to be lifted off the response itself — it is the only place the AI says what
    was actually wrong.
    """
    if response is None:
        return None

    try:
        return response.json()
    except Exception:
        pass

    try:
        text = (response.text or "").strip()
    except Exception:
        # A streamed response that was never read has no .text to fall back on.
        return None

    if not text:
        return None

    if len(text) > MAX_AI_ERROR_BODY_LENGTH:
        return text[:MAX_AI_ERROR_BODY_LENGTH] + "…"
    return text


def extract_ai_error_message(body: Any) -> Optional[str]:
    """Pull the human-readable sentence out of an AI error body.

    Handles the shapes the AI service actually returns: FastAPI's `{"detail": "..."}`,
    its validation form `{"detail": [{"loc": [...], "msg": "..."}]}`, and the
    `{"message": ...}` envelope this codebase uses. Anything unrecognised returns None so
    the caller can fall back to a generated message rather than surfacing a raw dict.
    """
    if isinstance(body, str):
        text = body.strip()
        # A bare-text body is only a message when it reads like one. A crashing AI service
        # answers with a traceback or an HTML page, and neither belongs in a field the user
        # reads — those stay in `details` and the caller generates a clean message instead.
        if text and len(text) <= 200 and "\n" not in text and not text.startswith("<"):
            return text
        return None

    if not isinstance(body, dict):
        return None

    detail = body.get("detail")

    if isinstance(detail, str) and detail.strip():
        return detail.strip()

    if isinstance(detail, list):
        parts = []
        for item in detail:
            if isinstance(item, dict):
                message = item.get("msg")
                if not message:
                    continue
                location = item.get("loc")
                if isinstance(location, (list, tuple)) and location:
                    parts.append(f"{'.'.join(str(part) for part in location)}: {message}")
                else:
                    parts.append(str(message))
            elif item:
                parts.append(str(item))
        if parts:
            return "; ".join(parts)

    for key in ("message", "error", "error_message", "msg"):
        value = body.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


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
            "Timed out trying to reach the AI service. It may be offline or unreachable.",
            ErrorCode.AI_CONNECT_TIMEOUT,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.ReadTimeout):
        return (
            "The AI service accepted the request but did not respond in time. It may still be processing — try again shortly.",
            ErrorCode.AI_READ_TIMEOUT,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.WriteTimeout):
        return (
            "Timed out while uploading the request to the AI service. This usually means a large file or a slow connection.",
            ErrorCode.AI_WRITE_TIMEOUT,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.PoolTimeout):
        return (
            "Too many AI requests are already in flight and no connection was free. Try again shortly.",
            ErrorCode.AI_POOL_TIMEOUT,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, httpx.TimeoutException):
        return (
            "The request to the AI service timed out.",
            ErrorCode.AI_TIMEOUT_ERROR,
            status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.ConnectError):
        return (
            "Unable to reach the AI service. It may be offline, or AI_BASE_URL may be misconfigured.",
            ErrorCode.AI_CONNECT_ERROR,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, httpx.NetworkError):
        return (
            "A network error interrupted the call to the AI service before it completed.",
            ErrorCode.AI_NETWORK_ERROR,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, httpx.RemoteProtocolError):
        return (
            "The AI service sent a malformed HTTP response.",
            ErrorCode.AI_REMOTE_PROTOCOL_ERROR,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, httpx.TooManyRedirects):
        return (
            "The AI service redirected too many times — the configured AI endpoint is likely wrong.",
            ErrorCode.AI_TOO_MANY_REDIRECTS,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, httpx.HTTPStatusError):
        response = getattr(exc, "response", None)
        ai_status = (
            response.status_code if response is not None else status.HTTP_502_BAD_GATEWAY
        )
        ai_message = extract_ai_error_message(read_ai_error_body(response))

        if ai_status in PASSTHROUGH_AI_STATUS_CODES:
            if ai_message:
                return (ai_message, ErrorCode.AI_HTTP_STATUS_ERROR, ai_status)

            return (
                f"AI service rejected the request with status {ai_status} and gave no reason",
                ErrorCode.AI_HTTP_STATUS_ERROR,
                ai_status,
            )

        if ai_message:
            return (
                f"The AI service failed with status {ai_status}: {ai_message}",
                ErrorCode.AI_UPSTREAM_FAILURE,
                status.HTTP_502_BAD_GATEWAY,
            )

        return (
            f"The AI service failed with status {ai_status} and gave no reason",
            ErrorCode.AI_UPSTREAM_FAILURE,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, httpx.RequestError):
        return (
            "The request to the AI service could not be completed.",
            ErrorCode.AI_REQUEST_ERROR,
            status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(exc, ValueError):
        return (
            "The AI service returned a response that was not valid JSON.",
            ErrorCode.AI_INVALID_RESPONSE_FORMAT,
            status.HTTP_400_BAD_REQUEST,
        )

    return (
        "An unexpected error occurred while contacting the AI service.",
        ErrorCode.AI_SERVICE_ERROR,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def handle_ai_exception(exc: Exception) -> AIException:
    """
    Translates an incoming httpx or ValueError exception into an AIException instance.
    """
    message, error_code, status_code = get_ai_message(exc)

    if isinstance(exc, httpx.HTTPStatusError):
        response = getattr(exc, "response", None)
        ai_status_code = response.status_code if response is not None else None
        details: Any = {
            "ai_status_code": ai_status_code,
            "ai_url": str(response.request.url) if response is not None and response.request else None,
            "ai_response": read_ai_error_body(response),
        }
        logger.error(
            "AI service returned %s for %s (surfaced as %s): %s",
            ai_status_code,
            details["ai_url"],
            status_code,
            details["ai_response"],
        )
    else:
        details = str(exc) or None
        logger.error("AI service call failed (%s): %s", type(exc).__name__, exc)

    return AIException(
        message=message,
        status_code=status_code,
        error_code=error_code,
        details=details,
    )
