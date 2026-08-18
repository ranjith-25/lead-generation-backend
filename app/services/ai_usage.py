import httpx

from app.core.connections.ai_connection import get_ai_client
from app.exceptions.ai_exception import handle_ai_exception
from app.responses.ai_usage import AIUsageMetricsResponse, AIUsageLogsResponse


async def get_cost_token_calls_service() -> AIUsageMetricsResponse:
    try:
        client = await get_ai_client()
        response = await client.get("/api/v1/dashboard/metrics")
        response.raise_for_status()
        body = response.json()
        return AIUsageMetricsResponse(
            message="Metrics fetched successfully",
            metrics=body.get("metrics", {}),
        )
    except httpx.HTTPError as exc:
        raise handle_ai_exception(exc)


async def get_logs_service() -> AIUsageLogsResponse:
    try:
        client = await get_ai_client()
        response = await client.get("/api/v1/dashboard/logs")
        response.raise_for_status()
        body = response.json()
        return AIUsageLogsResponse(
            message="Logs fetched successfully",
            returned_lines=body.get("returned_lines", 0),
            logs=body.get("logs", []),
        )
    except httpx.HTTPError as exc:
        raise handle_ai_exception(exc)