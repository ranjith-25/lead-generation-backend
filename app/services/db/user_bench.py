import logging
from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import BENCH_STATUS_NAME
from app.models.user_personal_info import UserPersonalInfo
from app.models.user_project import UserProject
from app.models.user_status import UserStatus


async def get_bench_status_id(db: AsyncSession) -> UUID | None:
    """The id of the `user_status` row that means "on bench", or None when it is absent.

    Matched case-insensitively on `displayName` against BENCH_STATUS_NAME because the row is
    admin-created data, not a schema value. Returning None rather than raising lets the caller
    decide — the auto-bench sync treats a missing row as "do nothing" so a lookup that was
    never seeded cannot fail an allocation delete.
    """
    try:
        result = await db.execute(
            select(UserStatus.id).where(
                UserStatus.displayName.ilike(BENCH_STATUS_NAME),
                UserStatus.is_active == True,
            )
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find the bench User Status")
        raise e


async def count_allocations_for_users(
    db: AsyncSession, user_ids: Sequence[UUID]
) -> dict[UUID, int]:
    """Live allocation counts for the given users, in one grouped query over `user_projects`.

    A user with no allocation rows produces no group and is therefore **absent** from the
    result — callers must read a missing key as zero, which is precisely the "should be
    benched" case.

    Soft-deleted allocations must not be counted: they are exactly the rows whose removal
    triggers this sync, and counting them would leave the freed user looking occupied so they
    were never benched at all.
    """
    if not user_ids:
        return {}

    try:
        result = await db.execute(
            select(UserProject.user_id, func.count(UserProject.user_project_id))
            .where(
                UserProject.user_id.in_(user_ids),
                UserProject.is_deleted.is_(False),
            )
            .group_by(UserProject.user_id)
        )
        return {row[0]: row[1] for row in result.all()}
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not count User Project allocations")
        raise e


async def get_working_status_map(
    db: AsyncSession, user_ids: Sequence[UUID]
) -> dict[UUID, tuple[UUID, str]]:
    """`{user_id: (working_status_id, display name)}` for the given users.

    One query serves both jobs the bench sync needs: skipping users already on bench, and
    naming them in the system log. Users without a `user_personal_info` row are absent — they
    have no `working_status_id` to move, so there is nothing to bench.
    """
    if not user_ids:
        return {}

    try:
        result = await db.execute(
            select(
                UserPersonalInfo.user_id,
                UserPersonalInfo.working_status_id,
                UserPersonalInfo.first_name,
                UserPersonalInfo.last_name,
            ).where(UserPersonalInfo.user_id.in_(user_ids))
        )

        return {
            row.user_id: (
                row.working_status_id,
                f"{row.first_name} {row.last_name}".strip() if row.last_name else row.first_name,
            )
            for row in result.all()
        }
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find User Personal Info working statuses")
        raise e


async def set_working_status(
    db: AsyncSession, user_ids: Sequence[UUID], status_id: UUID
) -> int:
    """Bulk-set `user_personal_info.working_status_id` for the given users; returns rowcount.

    Deliberately does **not** commit: the caller owns the transaction so that the system-log
    rows it stages beforehand land in the same commit as this write.
    """
    if not user_ids:
        return 0

    try:
        result = await db.execute(
            update(UserPersonalInfo)
            .where(UserPersonalInfo.user_id.in_(user_ids))
            .values(working_status_id=status_id)
            .execution_options(synchronize_session=False)
        )
        return result.rowcount or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update User Personal Info working status")
        raise e
