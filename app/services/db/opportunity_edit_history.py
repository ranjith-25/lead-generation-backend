from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import PageName
from app.models.opportunity_edit_history import OpportunityEditHistory


def stage_opportunity_edit_history(db: AsyncSession, history: OpportunityEditHistory) -> None:
    """Add the history row to the session WITHOUT committing.

    The caller's own commit (update_opportunity_db) flushes this alongside the opportunity
    update, so the edit and its audit row share one transaction and cannot diverge.
    """
    db.add(history)


async def get_opportunity_edit_history_db(
    db: AsyncSession,
    opportunity_id: UUID,
    page_name: PageName | None = None,
    page: int = 1,
    size: int = 10,
) -> tuple[list[OpportunityEditHistory], int]:

    query = select(OpportunityEditHistory).where(
        OpportunityEditHistory.opportunity_id == opportunity_id
    )

    if page_name:
        query = query.where(OpportunityEditHistory.page_name == page_name)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total_count = total_result.scalar() or 0

    query = (
        query.order_by(OpportunityEditHistory.edited_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    result = await db.execute(query)

    return list(result.scalars().all()), total_count
