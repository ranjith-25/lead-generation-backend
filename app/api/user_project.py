from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.user_project import (
    CreateUserProjectResponse,
    DeleteUserProjectResponse,
    GetUserProjectResponse,
    UpdateUserProjectResponse,
    UserProjectConfigurationsResponse,
)
from app.schemas.user_project import UserProjectCreate, UserProjectFilter, UserProjectUpdate
from app.services.user_project import (
    handle_create_user_project,
    handle_delete_user_project,
    handle_search_user_projects,
    handle_get_user_project_by_id,
    handle_get_user_project_configurations,
    handle_update_user_project,
)


router = APIRouter(prefix="/user-projects", tags=["User Projects"])


@router.post("/search")
async def search_user_projects(
    filters: UserProjectFilter | None = None,
    current_user: User = Depends(require_permission("user_projects", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetUserProjectResponse:
    return await handle_search_user_projects(
        db, current_user, filters.user_id if filters else None
    )


@router.get("/configurations")
async def get_user_project_configurations(
    current_user: User = Depends(require_permission("user_projects", "read")),
    db: AsyncSession = Depends(get_db),
) -> UserProjectConfigurationsResponse:
    return await handle_get_user_project_configurations(db, current_user)


@router.get("/{user_project_id}")
async def get_user_project_by_id(
    user_project_id: UUID,
    current_user: User = Depends(require_permission("user_projects", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetUserProjectResponse:
    return await handle_get_user_project_by_id(db, current_user, user_project_id)


@router.post("/")
async def create_user_project(
    user_project: UserProjectCreate,
    current_user: User = Depends(require_permission("user_projects", "create")),
    db: AsyncSession = Depends(get_db),
) -> CreateUserProjectResponse:
    return await handle_create_user_project(db, current_user, user_project)


@router.patch("/{user_project_id}")
async def update_user_project(
    user_project_id: UUID,
    user_project: UserProjectUpdate,
    current_user: User = Depends(require_permission("user_projects", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateUserProjectResponse:
    return await handle_update_user_project(db, current_user, user_project, user_project_id)


@router.delete("/{user_project_id}")
async def delete_user_project(
    user_project_id: UUID,
    current_user: User = Depends(require_permission("user_projects", "delete")),
    db: AsyncSession = Depends(get_db),
) -> DeleteUserProjectResponse:
    return await handle_delete_user_project(db, current_user, user_project_id)
