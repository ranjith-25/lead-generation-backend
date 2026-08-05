from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core.security import require_permission
from app.responses.job_roles import (
    GetJobRolesResponse,
    CreateJobRolesResponse,
    UpdateJobRolesResponse,
    DeleteJobRolesResponse,
)
from app.services.job_roles import (
    handle_create_job_role,
    handle_delete_job_role,
    handle_get_job_role_by_id,
    handle_get_job_roles,
    handle_update_job_role,
)
from app.schemas.job_roles import JobRolesCreate, JobRolesUpdate
from app.models.user import User
from app.api.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession

job_roles_router = APIRouter(prefix="/settings/configurations/job-roles", tags=["Job Roles"])


@job_roles_router.get("/")
async def get_all_job_roles(
    current_user: User = Depends(require_permission("job_roles", "read")),
    db: AsyncSession = Depends(get_db)
):
    response: GetJobRolesResponse = await handle_get_job_roles(db, current_user)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )


@job_roles_router.get("/{job_role_id}")
async def get_job_role_by_id(
    job_role_id: int,
    current_user: User = Depends(require_permission("job_roles", "read")),
    db: AsyncSession = Depends(get_db)
):
    response: GetJobRolesResponse = await handle_get_job_role_by_id(db, current_user, job_role_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )


@job_roles_router.post("/")
async def create_job_role(
    job_role: JobRolesCreate,
    current_user: User = Depends(require_permission("job_roles", "create")),
    db: AsyncSession = Depends(get_db)
):
    response: CreateJobRolesResponse = await handle_create_job_role(db, current_user, job_role)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )


@job_roles_router.put("/{job_role_id}")
async def update_job_role(
    job_role_id: int,
    job_role: JobRolesUpdate,
    current_user: User = Depends(require_permission("job_roles", "update")),
    db: AsyncSession = Depends(get_db)
):
    response: UpdateJobRolesResponse = await handle_update_job_role(db, current_user, job_role, job_role_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )


@job_roles_router.delete("/{job_role_id}")
async def delete_job_role(
    job_role_id: int,
    current_user: User = Depends(require_permission("job_roles", "delete")),
    db: AsyncSession = Depends(get_db)
):
    response: DeleteJobRolesResponse = await handle_delete_job_role(db, current_user, job_role_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200
    )
