from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from app.core.security import require_permission
from app.responses.project_domains import GetProjectDomainResponse,CreateProjectDomainResponse,UpdateProjectDomainResponse,DeleteProjectDomainResponse
from app.services.project_domains import handle_create_project_domain,handle_delete_project_domain,handle_get_project_domain_by_id,handle_get_project_domains,handle_update_project_domain
from app.schemas.project_domains import ProjectDomainCreate,ProjectDomainUpdate
from app.models.user import User
from app.api.deps import get_current_user,get_db 
from sqlalchemy.ext.asyncio import AsyncSession

project_domain_router = APIRouter(prefix="/settings/configurations/project-domains", tags=["Project Domains"])

@project_domain_router.get("/")
async def get_all_project_domains(
    current_user : User = Depends(require_permission("user_hierarchy","read")),
    db: AsyncSession = Depends(get_db)
    ):
    response : GetProjectDomainResponse = await handle_get_project_domains(db,current_user)
    return JSONResponse(
        content=response.model_dump(mode="json",exclude_none=True),
        status_code=200
    )

@project_domain_router.get("/{project_domain_id}")
async def get_project_domain_by_id(
    project_domain_id: int,
    current_user : User = Depends(require_permission("user_hierarchy","read")),
    db: AsyncSession = Depends(get_db)
    ):
    response : GetProjectDomainResponse = await handle_get_project_domain_by_id(db,current_user,projectDomainId)
    return JSONResponse(
        content=response.model_dump(mode="json",exclude_none=True),
        status_code=200
    )

@project_domain_router.post("/")
async def create_project_domain(
    project_domain : ProjectDomainCreate,
    current_user : User = Depends(require_permission("user_hierarchy","read")),
    db: AsyncSession = Depends(get_db)
    ):
    response : CreateProjectDomainResponse = await handle_create_project_domain(db,current_user,project_domain)
    return JSONResponse(
        content=response.model_dump(mode="json",exclude_none=True),
        status_code=200
    )

@project_domain_router.put("/{project_domain_id}")
async def update_project_domain(
    project_domain_id: int,
    project_domain : ProjectDomainUpdate,
    current_user : User = Depends(require_permission("user_hierarchy","read")),
    db: AsyncSession = Depends(get_db)
    ):
    response : UpdateProjectDomainResponse = await handle_update_project_domain(db,current_user,project_domain,project_domain_id)
    return JSONResponse(
        content=response.model_dump(mode="json",exclude_none=True),
        status_code=200
    )

@project_domain_router.delete("/{project_domain_id}")
async def delete_project_domain(
    project_domain_id: int,
    current_user : User = Depends(require_permission("user_hierarchy","read")),
    db: AsyncSession = Depends(get_db)
    ):
    response : DeleteProjectDomainResponse = await handle_delete_project_domain(db,current_user,project_domain_id)
    return JSONResponse(
        content=response.model_dump(mode="json",exclude_none=True),
        status_code=200
    )