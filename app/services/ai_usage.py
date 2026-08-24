from typing import Any
from uuid import UUID

import httpx
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.ai_connection import get_ai_client
from app.exceptions.ai_exception import AIValueError, handle_ai_exception
from app.responses.ai_usage import AIUsageMetricsResponse, AIUsageLogsResponse
from app.services.db.user import get_users_by_ids


def _as_body(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise AIValueError(
            message="The AI service returned an unexpected response body",
            details={"received_type": type(payload).__name__},
        )
    return payload

async def _resolve_usernames(db: AsyncSession, raw_logs: list[Any]) -> list[Any]:
    """Replace each entry's user_id with the corresponding user's full name, in place of `user`."""
    user_ids: set[UUID] = set()
    for entry in raw_logs:
        if isinstance(entry, dict) and entry.get("user_id"):
            try:
                user_ids.add(UUID(str(entry["user_id"])))
            except (ValueError, TypeError):
                continue

    if not user_ids:
        return raw_logs

    users = await get_users_by_ids(db, list(user_ids))
    name_by_id = {str(u.user_id): (u.fullName or u.email) for u in users}

    resolved: list[Any] = []
    for entry in raw_logs:
        if isinstance(entry, dict) and entry.get("user_id"):
            entry = {
                **entry,
                "user": name_by_id.get(str(entry["user_id"]), entry.get("user")),
            }
        resolved.append(entry)
    return resolved


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


async def get_logs_service(db: AsyncSession) -> AIUsageLogsResponse:
    try:
        client = get_ai_client()
        response = await client.get("/api/v1/dashboard/logs")
        response.raise_for_status()
        body = _as_body(response.json())

        raw_logs = await _resolve_usernames(db, body.get("logs") or [])
        
        return AIUsageLogsResponse(
            message="Logs fetched successfully",
            returned_lines=body.get("returned_lines") or 0,
            logs=raw_logs,
        )
    except httpx.HTTPError as exc:
        raise handle_ai_exception(exc)
    except ValidationError as exc:
        raise AIValueError(
            message="The AI service returned usage logs in an unexpected format",
            details=exc.errors(include_url=False, include_context=False),
        )
