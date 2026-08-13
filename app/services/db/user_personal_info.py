import logging
from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job_role import JobRole
from app.models.user_status import UserStatus
from app.models.user_personal_info import UserPersonalInfo
from app.models.profile_variant import ProfileVariant
from app.models.branch import Branch
from app.schemas.user_personal_info import UserPersonalInfoFilterRequest
from app.services.db.filters import apply_time_range


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
    db: AsyncSession, filters: UserPersonalInfoFilterRequest
) -> tuple[list[dict], int]:
    try:
        profiles_count_subquery = select(func.count(ProfileVariant.profile_variant_id)).where(ProfileVariant.created_by == UserPersonalInfo.user_id).scalar_subquery()
        
        query = select(
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
            profiles_count_subquery.label('profiles_count')
        ).outerjoin(User, UserPersonalInfo.user_id == User.user_id) \
         .outerjoin(JobRole, UserPersonalInfo.primary_role_id == JobRole.id) \
         .outerjoin(UserStatus, UserPersonalInfo.working_status_id == UserStatus.id) \
         .outerjoin(Branch, UserPersonalInfo.branch_id == Branch.id)

        query = apply_time_range(query, UserPersonalInfo.createdAt, filters.time_filter)

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

        if filters.primary_role:
            query = query.where(JobRole.roleName.in_(filters.primary_role))
        if filters.working_status:
            query = query.where(UserStatus.displayName.in_(filters.working_status))
        if filters.year_of_passout:
            query = query.where(UserPersonalInfo.year_of_passout.in_(filters.year_of_passout))
        if filters.team:
            query = query.where(User.fullName.in_(filters.team))
        if filters.branch:
            query = query.where(Branch.name.in_(filters.branch))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        query = query.offset((filters.page - 1) * filters.limit).limit(filters.limit)
        result = await db.execute(query)
        
        items = []
        for row in result:
            items.append({
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
            })

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


async def delete_user_personal_info(db: AsyncSession, user_id: UUID) -> UserPersonalInfo | None:
    try:
        result = await db.execute(select(UserPersonalInfo).where(UserPersonalInfo.user_id == user_id))
        db_personal_info = result.scalars().first()
        
        if not db_personal_info:
            return None
            
        await db.delete(db_personal_info)
        await db.commit()
        return db_personal_info
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(f"Could not delete User Personal Info for user_id: {user_id}")
        raise e

async def get_user_profile_filters(db: AsyncSession) -> dict:
    try:
        user_status_result = await db.execute(select(UserStatus.displayName).where(UserStatus.is_active == True))
        user_statuses = [row[0] for row in user_status_result]
        
        job_role_result = await db.execute(select(JobRole.roleName).where(JobRole.is_active == True))
        primary_roles = [row[0] for row in job_role_result]
        
        passout_result = await db.execute(
            select(UserPersonalInfo.year_of_passout)
            .distinct()
            .order_by(UserPersonalInfo.year_of_passout.desc())
        )
        years_of_passout = [row[0] for row in passout_result]
        
        branch_result = await db.execute(select(Branch.name).where(Branch.is_active == True))
        branches = [row[0] for row in branch_result]
        
        return {
            "user_status": user_statuses,
            "primary_role": primary_roles,
            "year_of_passout": years_of_passout,
            "branch": branches
        }
    except SQLAlchemyError as e:
        logging.exception("Could not fetch user profile filters")
        raise e
