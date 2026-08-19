import logging
from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.user import User
from app.models.job_role import JobRole
from app.models.user_status import UserStatus
from app.models.user_personal_info import UserPersonalInfo
from app.models.profile_variant import ProfileVariant
from app.models.branch import Branch
from app.schemas.user_personal_info import UserPersonalInfoFilterRequest
from app.services.db.filters import apply_date_filters, apply_sort

# Field names the API accepts for `sort_by`, mapped to the column each one sorts on.
USER_PERSONAL_INFO_SORTABLE = {
    "first_name": UserPersonalInfo.first_name,
    "last_name": UserPersonalInfo.last_name,
    "email": User.email,
    "date_of_birth": UserPersonalInfo.date_of_birth,
    "highest_qualification": UserPersonalInfo.highest_qualification,
    "year_of_passout": UserPersonalInfo.year_of_passout,
    "primary_role_name": JobRole.roleName,
    "working_status_name": UserStatus.displayName,
    "branch_name": Branch.name,
    "createdAt": UserPersonalInfo.createdAt,
}


def _join_name(first_name: str | None, last_name: str | None) -> str | None:
    """None rather than an empty string when the user has no manager."""
    if not first_name:
        return None
    return f"{first_name} {last_name}".strip() if last_name else first_name


async def create_user_personal_info(db: AsyncSession, personal_info: UserPersonalInfo) -> UserPersonalInfo:
    try:
        db.add(personal_info)
        await db.commit()
        await db.refresh(personal_info)
        return personal_info
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create User Personal Info")
        raise e


async def get_user_personal_info_by_user_id(db: AsyncSession, user_id: UUID) -> UserPersonalInfo | None:
    try:
        result = await db.execute(
            select(UserPersonalInfo).where(UserPersonalInfo.user_id == user_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not fetch User Personal Info for user_id: {user_id}")
        raise e


async def get_all_user_personal_info(
    db: AsyncSession, filters: UserPersonalInfoFilterRequest,applyPagination = True
) -> tuple[list[dict], int]:
    try:
        profiles_count_subquery = select(func.count(ProfileVariant.profile_variant_id)).where(ProfileVariant.created_by == UserPersonalInfo.user_id).scalar_subquery()

        columns = [
            UserPersonalInfo.user_id,
            User.email,
            UserPersonalInfo.first_name,
            UserPersonalInfo.last_name,
            JobRole.roleName.label('primary_role_name'),
            UserPersonalInfo.date_of_birth,
            UserPersonalInfo.highest_qualification,
            UserPersonalInfo.year_of_passout,
            UserStatus.displayName.label('working_status_name'),
            Branch.name.label('branch_name'),
            profiles_count_subquery.label('profiles_count'),
        ]

        # The manager is another row in the same two tables, so it needs its own aliases —
        # joining User/UserPersonalInfo again unaliased would collide with the joins above.
        reporting_user = aliased(User)
        reporting_info = aliased(UserPersonalInfo)

        if filters.is_reporting_to:
            columns.extend([
                User.reporting_to.label('reporting_to_id'),
                reporting_info.first_name.label('reporting_to_first_name'),
                reporting_info.last_name.label('reporting_to_last_name'),
            ])

        query = select(*columns) \
            .outerjoin(User, UserPersonalInfo.user_id == User.user_id) \
            .outerjoin(JobRole, UserPersonalInfo.primary_role_id == JobRole.id) \
            .outerjoin(UserStatus, UserPersonalInfo.working_status_id == UserStatus.id) \
            .outerjoin(Branch, UserPersonalInfo.branch_id == Branch.id)

        if filters.is_reporting_to:
            # Outer joins: a user with no manager still belongs in the list.
            query = query \
                .outerjoin(reporting_user, User.reporting_to == reporting_user.user_id) \
                .outerjoin(reporting_info, reporting_user.user_id == reporting_info.user_id)

        # Soft-deleted users drop out of the profile list. The join to `users` above is an
        # outer join, but user_personal_info.user_id is NOT NULL, so this never hides a row
        # that has no user.
        query = query.where(User.is_deleted.is_(False))

        query = apply_date_filters(
            query,
            UserPersonalInfo.createdAt,
            filters.time_filter,
            filters.from_date,
            filters.to_date,
        )

        if filters.search:
            search_term = f"%{filters.search.strip()}%"
            query = query.where(
                or_(
                    UserPersonalInfo.first_name.ilike(search_term),
                    UserPersonalInfo.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    UserPersonalInfo.date_of_birth.ilike(search_term),
                    JobRole.roleName.ilike(search_term),
                    UserPersonalInfo.highest_qualification.ilike(search_term),
                    UserPersonalInfo.specialization.ilike(search_term),
                )
            )

        # Every entity filter matches an id on user_personal_info itself. The joins above are
        # there to select and sort display names; nothing here leans on them.
        if filters.primary_role:
            query = query.where(UserPersonalInfo.primary_role_id.in_(filters.primary_role))
        if filters.working_status:
            query = query.where(UserPersonalInfo.working_status_id.in_(filters.working_status))
        if filters.year_of_passout:
            query = query.where(UserPersonalInfo.year_of_passout.in_(filters.year_of_passout))
        if filters.team:
            query = query.where(UserPersonalInfo.user_id.in_(filters.team))
        if filters.branch:
            query = query.where(UserPersonalInfo.branch_id.in_(filters.branch))
        # Straight off users.reporting_to rather than the aliased manager row, so the filter
        # does not depend on is_reporting_to having added those joins.
        if filters.reporting_to:
            query = query.where(User.reporting_to.in_(filters.reporting_to))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        query = apply_sort(
            query,
            USER_PERSONAL_INFO_SORTABLE,
            filters.sort_by,
            filters.order_by,
            default_column=UserPersonalInfo.createdAt,
        )

        ##Pagination
        if applyPagination:
            query = query.offset((filters.page - 1) * filters.limit).limit(filters.limit)
            
        result = await db.execute(query)

        items = []
        for row in result:
            item = {
                "user_id": row.user_id,
                "email": row.email,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "primary_role_name": row.primary_role_name,
                "date_of_birth": row.date_of_birth,
                "highest_qualification": row.highest_qualification,
                "year_of_passout": row.year_of_passout,
                "working_status_name": row.working_status_name,
                "branch_name": row.branch_name,
                "profiles_count": row.profiles_count
            }

            # Only present when asked for, so the keys stay absent — not null — otherwise.
            if filters.is_reporting_to:
                item["reporting_to_id"] = row.reporting_to_id
                item["reporting_to_name"] = _join_name(
                    row.reporting_to_first_name, row.reporting_to_last_name
                )

            items.append(item)

        return items, total or 0
    except SQLAlchemyError as e:
        logging.exception("Could not fetch User Personal Info list")
        raise e


async def update_user_personal_info(db: AsyncSession, update_data: dict, user_id: UUID) -> UserPersonalInfo | None:
    try:
        result = await db.execute(
            select(UserPersonalInfo).where(UserPersonalInfo.user_id == user_id)
        )
        db_personal_info = result.scalars().first()

        if not db_personal_info:
            return None

        for key, value in update_data.items():
            if hasattr(db_personal_info, key):
                setattr(db_personal_info, key, value)

        await db.commit()
        await db.refresh(db_personal_info)
        return db_personal_info
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not update User Personal Info for user_id: {user_id}")
        raise e


async def get_user_profile_filters(db: AsyncSession) -> dict:
    try:
        # Every option carries the id the filter matches on plus the label to render. Names
        # alone cannot address a row - they repeat, and they move under a rename.
        user_status_result = await db.execute(
            select(UserStatus.id, UserStatus.displayName)
            .where(UserStatus.is_active == True)
            .order_by(UserStatus.displayName)
        )
        user_statuses = [{"id": row.id, "name": row.displayName} for row in user_status_result]

        job_role_result = await db.execute(
            select(JobRole.id, JobRole.roleName)
            .where(JobRole.is_active == True)
            .order_by(JobRole.roleName)
        )
        primary_roles = [{"id": row.id, "name": row.roleName} for row in job_role_result]

        passout_result = await db.execute(
            select(UserPersonalInfo.year_of_passout)
            .distinct()
            .order_by(UserPersonalInfo.year_of_passout.desc())
        )
        years_of_passout = [row[0] for row in passout_result]

        branch_result = await db.execute(
            select(Branch.id, Branch.name)
            .where(Branch.is_active == True)
            .order_by(Branch.name)
        )
        branches = [{"id": row.id, "name": row.name} for row in branch_result]

        # Only users somebody actually reports to - listing every user would offer filter
        # values that can only ever return an empty page.
        manager_ids = select(User.reporting_to).where(User.reporting_to.isnot(None)).distinct()
        manager_result = await db.execute(
            select(
                User.user_id,
                UserPersonalInfo.first_name,
                UserPersonalInfo.last_name,
            )
            .outerjoin(UserPersonalInfo, UserPersonalInfo.user_id == User.user_id)
            .where(User.user_id.in_(manager_ids), User.is_deleted.is_(False))
            .order_by(UserPersonalInfo.first_name, UserPersonalInfo.last_name)
        )
        reporting_to = [
            {
                "id": row.user_id,
                # Built from the same first/last pair the list rows use for reporting_to_name,
                # so the dropdown label matches the column. `User.fullName` cannot be selected
                # here - it is a plain Python property, not a column - so its "Unknown User"
                # fallback is spelled out instead.
                "name": _join_name(row.first_name, row.last_name) or "Unknown User",
            }
            for row in manager_result
        ]

        return {
            "user_status": user_statuses,
            "primary_role": primary_roles,
            "year_of_passout": years_of_passout,
            "branch": branches,
            "reporting_to": reporting_to,
        }
    except SQLAlchemyError as e:
        logging.exception("Could not fetch user profile filters")
        raise e
