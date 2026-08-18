from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_log import SystemLog
from app.schemas.system_log import SystemLogFilterRequest


def stage_system_log(db: AsyncSession, log: SystemLog) -> None:
    """Add the log row to the session WITHOUT committing.

    The business action's own commit flushes this alongside it, so the action and its audit
    row share one transaction and cannot diverge. Read-only actions (downloads, exports)
    have no such commit and must issue their own — see `log_activity`.
    """
    db.add(log)


async def get_system_logs_db(
    db: AsyncSession, filters: SystemLogFilterRequest
) -> tuple[list[SystemLog], int]:

    query = select(SystemLog)

    if filters.module:
        query = query.where(SystemLog.module == filters.module)

    if filters.action:
        query = query.where(SystemLog.action == filters.action)

    if filters.performed_by:
        query = query.where(SystemLog.performed_by == filters.performed_by)

    if filters.from_date:
        query = query.where(SystemLog.performed_at >= filters.from_date)

    if filters.to_date:
        query = query.where(SystemLog.performed_at <= filters.to_date)

    if filters.search:
        term = f"%{filters.search.strip()}%"
        query = query.where(
            or_(
                SystemLog.description.ilike(term),
                SystemLog.performed_by_name.ilike(term),
            )
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total_count = total_result.scalar() or 0

    query = (
        query.order_by(SystemLog.performed_at.desc())
        .offset((filters.page - 1) * filters.size)
        .limit(filters.size)
    )

    result = await db.execute(query)

    return list(result.scalars().all()), total_count


async def get_system_log_by_id(db: AsyncSession, log_id: UUID) -> SystemLog | None:
    result = await db.execute(select(SystemLog).where(SystemLog.id == log_id))
    return result.scalars().first()
