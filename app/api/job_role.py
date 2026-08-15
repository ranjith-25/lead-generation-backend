from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.job_role import (
    CreateJobRoleResponse,
    DeleteJobRoleResponse,
    GetJobRoleResponse,
    UpdateJobRoleResponse,
)
from app.schemas.job_role import JobRoleCreate, JobRoleUpdate
from app.services.job_role import (
    handle_create_job_role,
    get_top_job_roles_service,
    handle_delete_job_role,
    handle_get_all_job_roles,
    handle_get_job_role_by_id,
    handle_update_job_role,
)

router = APIRouter(prefix="/job-roles", tags=["Job Role"])


@router.get("/")
async def get_all_job_roles(
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    limit: int | None = None
) -> GetJobRoleResponse:
    return await handle_get_all_job_roles(db, page, limit)

@router.get("/top-roles")
async def get_top_job_roles(
    count : int | None = 5,
    db: AsyncSession = Depends(get_db),
):
    return await get_top_job_roles_service(db, count)

@router.get("/{id}")
async def get_job_role_by_id(
    id: UUID,
    current_user: User = Depends(require_permission("job_roles", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetJobRoleResponse:
    return await handle_get_job_role_by_id(db, current_user, id)


@router.post("/")
async def create_job_role(
    job_role: JobRoleCreate,
    current_user: User = Depends(require_permission("job_roles", "create")),
    db: AsyncSession = Depends(get_db),
) -> CreateJobRoleResponse:
    return await handle_create_job_role(db, current_user, job_role)


@router.put("/{id}")
async def update_job_role(
    id: UUID,
    job_role: JobRoleUpdate,
    current_user: User = Depends(require_permission("job_roles", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateJobRoleResponse:
    return await handle_update_job_role(db, current_user, job_role, id)


@router.delete("/{id}")
async def delete_job_role(
    id: UUID,
    current_user: User = Depends(require_permission("job_roles", "delete")),
    db: AsyncSession = Depends(get_db),
) -> DeleteJobRoleResponse:
    return await handle_delete_job_role(db, current_user, id)
