import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import (
    LOG_ACTION_LABELS,
    LOG_ACTION_MODULES,
    LOG_ACTION_VERBS,
    LOG_MODULE_LABELS,
    SYSTEM_LOG_DESCRIPTION,
    SYSTEM_LOG_DESCRIPTION_WITH_ENTITY,
    SYSTEM_LOG_MAX_DESCRIPTION_LENGTH,
    LogAction,
    LogModule,
)
from app.exceptions.system_log import SystemLogNotFoundException
from app.models.system_log import SystemLog
from app.models.user import User
from app.responses.system_log import SystemLogPaginatedResponse
from app.schemas.system_log import (
    SystemLogDetailRead,
    SystemLogFilterRequest,
    SystemLogRead,
)
from app.services.db.system_log import (
    get_system_log_by_id,
    get_system_logs_db,
    stage_system_log,
)
from app.services.db.user import get_user_by_id

logger = logging.getLogger(__name__)

UNKNOWN_USER = "Unknown User"


def _coerce_json(value: Any) -> Any:
    """JSONB-safe coercion, reusing the edit-history rules (UUID, datetime, Decimal, Enum).

    Imported inside the function so adding a `log_activity` call to a service never drags a
    new module-level import chain into that service's import graph.
    """
    from app.services.opportunity_edit_history import _json_safe

    return _json_safe(value)


async def _resolve_actor(db: AsyncSession, user: User | UUID | str | None) -> tuple[UUID | None, str]:
    """(user id, name snapshot) from whichever form the call site already has to hand."""
    if user is None:
        return None, UNKNOWN_USER

    if isinstance(user, User):
        return user.user_id, user.fullName or UNKNOWN_USER

    try:
        user_id = UUID(str(user))
    except (ValueError, TypeError):
        return None, UNKNOWN_USER

    actor = await get_user_by_id(db, user_id)
    return user_id, (actor.fullName if actor else UNKNOWN_USER)


def _build_description(
    action: LogAction, actor_name: str, entity_name: str | None
) -> str:
    verb = LOG_ACTION_VERBS.get(action) or LOG_ACTION_LABELS.get(action, action.value).lower()

    if entity_name:
        sentence = SYSTEM_LOG_DESCRIPTION_WITH_ENTITY.format(
            user=actor_name, verb=verb, entity=entity_name
        )
    else:
        sentence = SYSTEM_LOG_DESCRIPTION.format(user=actor_name, verb=verb)

    return sentence[:SYSTEM_LOG_MAX_DESCRIPTION_LENGTH]


async def log_activity(
    db: AsyncSession,
    action: LogAction,
    user: User | UUID | str | None,
    module: LogModule | None = None,
    entity_type: str | None = None,
    entity_id: UUID | str | None = None,
    entity_name: str | None = None,
    description: str | None = None,
    details: dict | None = None,
    commit: bool = False,
) -> None:
    """Stage one system-log row for a curated business event.

    Two rules follow from staging rather than committing:

    1. Call this BEFORE the DB-layer function that commits, so that commit flushes the row.
    2. For deletes, read `entity_id` / `details` off the object while the row still exists.

    `commit=True` is for the read-only actions (`PROFILE_DOWNLOADED`,
    `CASE_STUDY_DOWNLOADED`, `CSV_EXPORTED`) which have no business write to ride along on.

    Auditing must never be the reason a working endpoint starts failing, so a fault while
    composing the row is logged and swallowed rather than raised at the call site.
    """
    try:
        actor_id, actor_name = await _resolve_actor(db, user)
        resolved_module = module or LOG_ACTION_MODULES.get(action)

        if resolved_module is None:
            logger.warning("No module mapped for system log action %s", action)
            return

        try:
            resolved_entity_id = UUID(str(entity_id)) if entity_id else None
        except (ValueError, TypeError):
            resolved_entity_id = None

        stage_system_log(
            db,
            SystemLog(
                action=action,
                module=resolved_module,
                performed_by=actor_id,
                performed_by_name=actor_name,
                entity_type=entity_type,
                entity_id=resolved_entity_id,
                description=(description or _build_description(action, actor_name, entity_name))[
                    :SYSTEM_LOG_MAX_DESCRIPTION_LENGTH
                ],
                details=_coerce_json(details) if details else None,
            ),
        )

        if commit:
            await db.commit()

    except Exception:
        logger.exception("Failed to record system log for action %s", action)


# ---------------------------------------------------------------------------
# Read side
# ---------------------------------------------------------------------------


def _build_read(row: SystemLog) -> dict:
    return {
        "id": row.id,
        "timestamp": row.performed_at,
        "performed_by": row.performed_by,
        "performed_by_name": row.performed_by_name or UNKNOWN_USER,
        "action": row.action,
        "action_label": LOG_ACTION_LABELS.get(row.action, str(row.action)),
        "module": row.module,
        "module_label": LOG_MODULE_LABELS.get(row.module, str(row.module)),
        "description": row.description,
    }


async def get_system_logs_service(
    db: AsyncSession, filters: SystemLogFilterRequest
) -> SystemLogPaginatedResponse:

    logs, total = await get_system_logs_db(db, filters)

    return SystemLogPaginatedResponse(
        data=[SystemLogRead(**_build_read(row)) for row in logs],
        total=total,
        page=filters.page,
        size=filters.size,
        total_pages=math.ceil(total / filters.size) if total > 0 else 1,
    )


async def get_system_log_detail_service(
    db: AsyncSession, log_id: UUID
) -> SystemLogDetailRead:

    row = await get_system_log_by_id(db, log_id)
    if not row:
        raise SystemLogNotFoundException(log_id)

    return SystemLogDetailRead(
        **_build_read(row),
        entity_type=row.entity_type,
        entity_id=row.entity_id,
        details=row.details,
    )
