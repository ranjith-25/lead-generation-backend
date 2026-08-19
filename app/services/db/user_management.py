import logging
from sqlalchemy import select, or_, func, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from uuid import UUID

from app.models.role import Role
from app.models.user import User
from app.models.job_role import JobRole
from app.models.user_personal_info import UserPersonalInfo
from app.schemas.user_personal_info import UserManagementFilterRequest
from app.services.db.filters import apply_sort, apply_time_range
from app.services.db.user import resolve_live_manager

# Field names the API accepts for `sort_by`, mapped to the column each one sorts on.
USER_MANAGEMENT_SORTABLE = {
    "first_name": UserPersonalInfo.first_name,
    "last_name": UserPersonalInfo.last_name,
    "email": User.email,
    "role_name": Role.roleName,
    "createdAt": UserPersonalInfo.createdAt,
}


async def get_all_user_management_info(
    db: AsyncSession, filters: UserManagementFilterRequest
) -> tuple[list[dict], int]:
    try:
        query = select(
            UserPersonalInfo.user_id,
            User.email,
            UserPersonalInfo.first_name,
            UserPersonalInfo.last_name,
            Role.roleName.label('role_name')
        ).outerjoin(User, UserPersonalInfo.user_id == User.user_id) \
         .outerjoin(Role, User.role_id == Role.role_id)

        # Soft-deleted users are not manageable, so they leave this grid too.
        query = query.where(User.is_deleted.is_(False))

        query = apply_time_range(query, UserPersonalInfo.createdAt, filters.time_filter)

        if filters.search:
            search_term = f"%{filters.search.strip()}%"
            query = query.where(
                or_(
                    UserPersonalInfo.first_name.ilike(search_term),
                    UserPersonalInfo.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    Role.roleName.ilike(search_term)
                )
            )

        if getattr(filters, 'role_id', None):
            query = query.where(User.role_id == filters.role_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        query = apply_sort(
            query,
            USER_MANAGEMENT_SORTABLE,
            filters.sort_by,
            filters.order_by,
            default_column=UserPersonalInfo.createdAt,
        )

        query = query.offset((filters.page - 1) * filters.limit).limit(filters.limit)
        result = await db.execute(query)
        
        items = []
        for row in result:
            full_name = row.first_name
            if row.last_name:
                full_name = f"{row.first_name} {row.last_name}"
                
            items.append({
                "user_id": row.user_id,
                "full_name": full_name,
                "email": row.email,
                "role_name": row.role_name
            })

        return items, total or 0
    except SQLAlchemyError as e:
        logging.exception("Could not fetch User Management list")
        raise e

async def update_user_role_and_reporting_to(
    db: AsyncSession,
    user_id: UUID,
    role_id: UUID,
    reporting_to: UUID | None
) -> None:
    try:
        from uuid import UUID
        # `users.role_id` is NOT NULL, so a None slipping through here would only surface on
        # commit as an opaque IntegrityError naming a constraint the caller never mentioned.
        # Reject it up front, the same way the missing-user case below is rejected.
        if role_id is None:
            raise ValueError("role_id is required and cannot be null")

        # Filtered: a soft-deleted user is not manageable, and re-pointing their reporting_to
        # would put them back into the hierarchy tree.
        result = await db.execute(
            select(User).where(User.user_id == user_id, User.is_deleted.is_(False))
        )
        user = result.scalars().first()
        if not user:
            raise ValueError(f"User with id {user_id} not found")
            
        user.role_id = role_id
        user.reporting_to = reporting_to
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not update user {user_id}")
        raise e


async def get_live_user_ids(db: AsyncSession) -> list[UUID]:
    """Every non-soft-deleted user id.

    The bench backfill needs the whole live population as its candidate set - it is the only
    way to reach the users who were already sitting at zero allocations before the auto-bench
    sync existed. Ids only: `sync_bench_status` re-reads whatever else it needs.
    """
    try:
        result = await db.execute(
            select(User.user_id).where(User.is_deleted.is_(False))
        )
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logging.exception("Could not fetch the live user ids")
        raise e


async def repair_dangling_reporting_to(db: AsyncSession) -> dict[str, int]:
    """Re-point every live user whose manager is soft-deleted (or gone) onto a live ancestor.

    `soft_delete_user` reparents a deleted manager's reports, but only rows that existed at
    that moment. A manager deleted afterwards, a row restored by hand, or any user written
    before that reparenting was made dead-ancestor-aware leaves a live user pointing at a
    `is_deleted = true` row - which `getAllUsers` filters out, so `handleGetHierarchy` silently
    promotes that user to a root instead of showing the break. This is the sweep that fixes the
    accumulated damage; the repo forbids maintenance scripts, so it is exposed as an endpoint.

    The counts returned, exactly:

    * `scanned`   - live users found holding a dangling link, i.e. the rows this pass examined.
                    Users whose `reporting_to` is NULL or points at a live manager are never
                    selected and are therefore **not** counted here.
    * `repaired`  - of those, the ones re-pointed at a live ancestor found further up the chain.
    * `orphaned`  - of those, the ones set to NULL because no live ancestor exists (the chain
                    ends at a root, is deleted all the way up, or loops).

    `scanned == repaired + orphaned` always holds. One commit at the end, so a failure part-way
    leaves the hierarchy exactly as it was.
    """
    try:
        # Only the broken rows: a self-join that keeps a live user when their manager row is
        # either soft-deleted or missing altogether (the outer join then yields NULL). Walking
        # up from every user in the table instead would be one query per user for no reason.
        manager = aliased(User)
        result = await db.execute(
            select(User.user_id, User.reporting_to)
            .outerjoin(manager, manager.user_id == User.reporting_to)
            .where(
                User.is_deleted.is_(False),
                User.reporting_to.is_not(None),
                or_(manager.user_id.is_(None), manager.is_deleted.is_(True)),
            )
        )
        dangling = result.all()

        if not dangling:
            return {"scanned": 0, "repaired": 0, "orphaned": 0}

        # Whole teams share one dead manager, so the upward walk is memoised on that id - the
        # cost becomes one walk per broken *manager* rather than one per affected user.
        resolved: dict[UUID, UUID | None] = {}
        # Grouped by destination so the writes are a handful of bulk updates, not one per user.
        by_target: dict[UUID | None, list[UUID]] = {}

        for user_id, dead_manager_id in dangling:
            if dead_manager_id not in resolved:
                resolved[dead_manager_id] = await resolve_live_manager(db, dead_manager_id)

            target = resolved[dead_manager_id]
            # A cycle can hand back the very user being repaired; that row is live, so
            # `resolve_live_manager` legitimately stops on it. Writing it would make the user
            # their own manager, so this case is an orphan instead.
            if target == user_id:
                target = None

            by_target.setdefault(target, []).append(user_id)

        repaired = 0
        orphaned = 0
        for target, user_ids in by_target.items():
            await db.execute(
                update(User)
                .where(User.user_id.in_(user_ids))
                .values(reporting_to=target)
                .execution_options(synchronize_session=False)
            )
            if target is None:
                orphaned += len(user_ids)
            else:
                repaired += len(user_ids)

        await db.commit()

        logging.info(
            "Reporting hierarchy repair: scanned %s, repaired %s, orphaned %s",
            len(dangling),
            repaired,
            orphaned,
        )
        return {"scanned": len(dangling), "repaired": repaired, "orphaned": orphaned}
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not repair the dangling reporting_to links")
        raise e
