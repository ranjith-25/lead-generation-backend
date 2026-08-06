from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
    handle_delete_job_role,
    handle_get_all_job_roles,
    handle_get_job_role_by_id,
    handle_update_job_role,
)

router = APIRouter(prefix="/job-roles", tags=["Job Role"])


@router.get("/")
async def get_all_job_roles(
    current_user: User = Depends(require_permission("job_role", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetJobRoleResponse:
    return await handle_get_all_job_roles(db, current_user)


@router.get("/{id}")
async def get_job_role_by_id(
    id: int,
    current_user: User = Depends(require_permission("job_role", "read")),
    db: AsyncSession = Depends(get_db),
) -> GetJobRoleResponse:
    return await handle_get_job_role_by_id(db, current_user, id)


@router.post("/")
async def create_job_role(
    job_role: JobRoleCreate,
    current_user: User = Depends(require_permission("job_role", "create")),
    db: AsyncSession = Depends(get_db),
) -> CreateJobRoleResponse:
    return await handle_create_job_role(db, current_user, job_role)


@router.put("/{id}")
async def update_job_role(
    id: int,
    job_role: JobRoleUpdate,
    current_user: User = Depends(require_permission("job_role", "update")),
    db: AsyncSession = Depends(get_db),
) -> UpdateJobRoleResponse:
    return await handle_update_job_role(db, current_user, job_role, id)


@router.delete("/{id}")
async def delete_job_role(
    id: int,
    current_user: User = Depends(require_permission("job_role", "delete")),
    db: AsyncSession = Depends(get_db),
) -> DeleteJobRoleResponse:
    return await handle_delete_job_role(db, current_user, id)
