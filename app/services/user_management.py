import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_personal_info import UserManagementFilterRequest
from app.schemas.user_management import (
    UserManagementListRead,
    UserManagementPaginatedResponse
)
from app.services.db.user_management import get_all_user_management_info

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
