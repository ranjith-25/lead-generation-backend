import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_personal_info import UserManagementFilterRequest
from app.schemas.user_management import (
    UserManagementListRead,
    UserManagementPaginatedResponse
)
from app.services.db.user_management import (
    get_all_user_management_info,
    get_live_user_ids,
    repair_dangling_reporting_to,
    update_user_role_and_reporting_to
)
from app.services.db.user import get_user_by_id
from app.services.user_project import sync_bench_status
from app.config import LogAction
from app.services.system_log import log_activity
from app.schemas.user_management import UpdateUserRoleRequest
from app.responses.base import BaseResponse
from app.responses.user_management import RepairReportingHierarchyResponse
from uuid import UUID
from fastapi import HTTPException

async def handle_get_all_user_management(
    db: AsyncSession, current_user: User, filters: UserManagementFilterRequest
) -> UserManagementPaginatedResponse:
    try:
        items, total = await get_all_user_management_info(db, filters)
        
        return UserManagementPaginatedResponse(
            items=[UserManagementListRead(**item) for item in items],
            total=total,
            page=filters.page,
            limit=filters.limit,
            total_pages=(total + filters.limit - 1) // filters.limit if total > 0 else 1
        )
    except Exception as e:
        logging.exception("Some error occurred while getting User Management list")
        raise e

async def handle_update_user_role(
    db: AsyncSession,
    target_user_id: str,
    update_data: UpdateUserRoleRequest,
    user_id: UUID | None = None,
) -> BaseResponse:
    try:
        user_uuid = UUID(target_user_id)

        target_user = await get_user_by_id(db, user_uuid)
        if target_user and target_user.role_id != update_data.role_id:
            await log_activity(
                db,
                LogAction.USER_ROLE_CHANGED,
                user_id,
                entity_type="user",
                entity_id=user_uuid,
                entity_name=target_user.fullName,
                details={
                    "previousRoleID": target_user.role_id,
                    "newRoleID": update_data.role_id,
                },
            )

        await update_user_role_and_reporting_to(
            db, user_uuid, update_data.role_id, update_data.reporting_to
        )
        return BaseResponse(success=True, message="User role updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.exception("Some error occurred while updating user role")
        raise HTTPException(status_code=500, detail="Could not update user role")

async def handle_repair_reporting_hierarchy(
    db: AsyncSession, current_user: User
) -> RepairReportingHierarchyResponse:
    """Run the two org-integrity sweeps that would otherwise need a maintenance script.

    First the reporting repair: live users pointing at a soft-deleted (or missing) manager are
    moved onto their nearest live ancestor, or detached when there is none. Then the bench
    backfill: every live user currently holding zero project allocations and not already on
    bench is moved to the bench status - the state the allocation and project delete paths keep
    up to date from now on, applied once to the users who predate them.

    The two halves commit separately and deliberately. The bench pass is wrapped so that a
    failure inside it - a missing `On Bench` lookup row, a personal-info write that will not
    take - is logged and reported as `benched: 0` rather than discarding a reporting repair that
    has already committed. The endpoint is idempotent, so re-running it after fixing the cause
    costs nothing.
    """
    try:
        counts = await repair_dangling_reporting_to(db)

        benched = 0
        try:
            live_user_ids = await get_live_user_ids(db)
            # sync_bench_status already owns the whole policy - zero allocations only, skip the
            # already-benched, never un-bench - so the backfill is that same call over everyone.
            benched = await sync_bench_status(db, live_user_ids, current_user.user_id)
        except Exception:
            logging.exception(
                "Reporting hierarchy repaired, but the bench backfill failed - reporting "
                "counts are committed and the backfill can be re-run"
            )

        # `commit=True` because both writes above have already committed - there is no business
        # write left for this row to ride along on. No `entity_type`/`entity_id`: a sweep has no
        # single subject, and filing it under one arbitrary user would misread as an edit to
        # that user.
        await log_activity(
            db,
            LogAction.USER_HIERARCHY_REPAIRED,
            current_user,
            description=(
                f"{current_user.fullName} repaired the reporting hierarchy - "
                f"{counts['repaired']} re-pointed, {counts['orphaned']} orphaned, "
                f"{benched} moved to bench"
            ),
            details={
                "operation": "repair_reporting_hierarchy",
                "scanned": counts["scanned"],
                "repaired": counts["repaired"],
                "orphaned": counts["orphaned"],
                "benched": benched,
            },
            commit=True,
        )

        return RepairReportingHierarchyResponse(
            message=(
                f"Reporting hierarchy repaired: {counts['repaired']} user(s) re-pointed and "
                f"{counts['orphaned']} orphaned out of {counts['scanned']} dangling link(s); "
                f"{benched} user(s) moved to bench"
            ),
            scanned=counts["scanned"],
            repaired=counts["repaired"],
            orphaned=counts["orphaned"],
            benched=benched,
        )
    except Exception as e:
        logging.exception("Some error occurred while repairing the reporting hierarchy")
        raise e
