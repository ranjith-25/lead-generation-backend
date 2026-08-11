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
    update_user_role_and_reporting_to
)
from app.schemas.user_management import UpdateUserRoleRequest
from app.responses.base import BaseResponse
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
    db: AsyncSession, target_user_id: str, update_data: UpdateUserRoleRequest
) -> BaseResponse:
    try:
        user_uuid = UUID(target_user_id)
        await update_user_role_and_reporting_to(
            db, user_uuid, update_data.role_id, update_data.reporting_to
        )
        return BaseResponse(success=True, message="User role updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.exception("Some error occurred while updating user role")
        raise HTTPException(status_code=500, detail="Could not update user role")
