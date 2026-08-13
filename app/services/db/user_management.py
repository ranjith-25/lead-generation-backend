import logging
from sqlalchemy import select, or_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.role import Role
from app.models.user import User
from app.models.job_role import JobRole
from app.models.user_personal_info import UserPersonalInfo
from app.schemas.user_personal_info import UserManagementFilterRequest
from app.services.db.filters import apply_time_range


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
        result = await db.execute(select(User).where(User.user_id == user_id))
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
