from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.connections.postgres import get_db
from app.models.user import User
from app.responses.base import BaseResponse
from app.responses.project import ProjectListResponse
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project import (
    create_project_service,
    delete_project_service,
    get_all_projects_service,
    get_project_case_study_service,
    get_project_service,
    update_project_service,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    return await get_all_projects_service(db, limit, page)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate = Depends(ProjectCreate.as_form),
    case_study: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    return await create_project_service(db, project, case_study)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    return await get_project_service(db, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project: ProjectUpdate = Depends(ProjectUpdate.as_form),
    case_study: UploadFile | None = File(None),
    remove_case_study: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    return await update_project_service(db, project_id, project, case_study, remove_case_study)


@router.get("/{project_id}/case-study")
async def download_case_study(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    document = await get_project_case_study_service(db, project_id)
    return FileResponse(document, filename=document.name)


@router.delete("/{project_id}", response_model=BaseResponse)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    return await delete_project_service(db, project_id)
