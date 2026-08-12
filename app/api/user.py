from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from typing import Optional

from uuid import UUID
from app.core.security import require_permission
from app.models.user import User
from app.schemas.user import UserRoleRead
from app.services.db.user import get_all_user_by_role
from app.core.connections.postgres import get_db

router = APIRouter(prefix="/users", tags=["User"])

@router.post('/user-roles', response_model=list[UserRoleRead])
async def get_users_with_roles(
    roles: Optional[list[UUID]],
    db: AsyncSession = Depends(get_db),
    current_user: User =  Depends(get_current_user),
):
    return await get_all_user_by_role(db, roles)