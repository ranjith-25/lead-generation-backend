from typing import Any

import httpx
from pydantic import ValidationError

from app.core.connections.ai_connection import get_ai_client
from app.exceptions.ai_exception import AIValueError, handle_ai_exception
from app.responses.ai_usage import AIUsageMetricsResponse, AIUsageLogsResponse


def _as_body(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AIValueError(
            message="The AI service returned an unexpected response body",
            details={"received_type": type(payload).__name__},
        )
    return payload


async def get_cost_token_calls_service() -> AIUsageMetricsResponse:
    try:
        client = get_ai_client()
        response = await client.get("/api/v1/dashboard/metrics")
        response.raise_for_status()
        body = _as_body(response.json())
        return AIUsageMetricsResponse(
            message="Metrics fetched successfully",
            metrics=body.get("metrics") or {},
        )
    except httpx.HTTPError as exc:
        raise handle_ai_exception(exc)
    except ValidationError as exc:
        raise AIValueError(
            message="The AI service returned usage metrics in an unexpected format",
            details=exc.errors(include_url=False, include_context=False),
        )


async def get_logs_service() -> AIUsageLogsResponse:
    try:
        client = get_ai_client()
        response = await client.get("/api/v1/dashboard/logs")
        response.raise_for_status()
        body = _as_body(response.json())
        return AIUsageLogsResponse(
            message="Logs fetched successfully",
            returned_lines=body.get("returned_lines") or 0,
            logs=body.get("logs") or [],
        )
    except httpx.HTTPError as exc:
        raise handle_ai_exception(exc)
    except ValidationError as exc:
        raise AIValueError(
            message="The AI service returned usage logs in an unexpected format",
            details=exc.errors(include_url=False, include_context=False),
        )
