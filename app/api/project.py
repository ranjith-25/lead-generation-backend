from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_current_user
from app.config import SortOrder, TimeRange
from app.core.connections.postgres import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.base import BaseResponse
from app.responses.project import ProjectListResponse, ProjectFilterResponse 
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate, ProjectFilters
from app.services.project import (
    create_project_service,
    delete_project_service,
    get_all_projects_service,
    get_project_case_study_service,
    get_project_service,
    update_project_service,
    get_project_filters
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    time_filter: TimeRange | None = Query(None),
    sort_by: str | None = Query(None, description="Field to sort on; unsupported names are ignored"),
    order_by: SortOrder | None = Query(None),
    current_user: User = Depends(require_permission("projects", "read")),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    return await get_all_projects_service(
        db,
        ProjectFilters(
            page=page,
            limit=limit,
            time_filter=time_filter,
            sort_by=sort_by,
            order_by=order_by,
        ),
    )


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate = Depends(ProjectCreate.as_form),
    case_study: UploadFile | None = File(None),
    current_user: User = Depends(require_permission("projects", "create")),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    return await create_project_service(db, project, current_user.user_id, case_study)

@router.post("/get_all", response_model=ProjectListResponse)
async def get_all_projects(
    filters: ProjectFilters,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    return await get_all_projects_service(db, filters)

@router.get("/filter-values", response_model=ProjectFilterResponse)
async def get_filter_values(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("projects", "read"))
):
    return await get_project_filters(db)

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(require_permission("projects", "read")),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    return await get_project_service(db, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID,
    project: ProjectUpdate = Depends(ProjectUpdate.as_form),
    case_study: UploadFile | None = File(None),
    remove_case_study: bool = Form(False),
    current_user: User = Depends(require_permission("projects", "update")),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    return await update_project_service(db, project_id, project, case_study, remove_case_study)


@router.get("/{project_id}/case-study")
async def download_case_study(
    project_id: UUID,
    current_user: User = Depends(require_permission("projects", "read")),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    document = await get_project_case_study_service(db, project_id)
    return FileResponse(document, filename=document.name)

@router.delete("/{project_id}", response_model=BaseResponse)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(require_permission("projects", "delete")),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    return await delete_project_service(db, project_id)
