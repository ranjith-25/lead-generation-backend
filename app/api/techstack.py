from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.techstack import (
    CreateTechStackResponse,
    DeleteTechStackResponse,
    GetTechStackResponse,
    UpdateTechStackResponse,
)
from app.schemas.techstack import TechStackCreate, TechStackUpdate
from app.services.techstack import (
    handle_create_techstack,
    handle_delete_techstack,
    handle_get_techstack_by_id,
    handle_get_techstacks,
    handle_update_techstack,
)

from app.schemas.techstack import TechStackRead

techstack_router = APIRouter(prefix="/settings/configurations/techstacks", tags=["Tech Stacks"])


@techstack_router.get("/")
async def get_all_techstacks(
    current_user: User = Depends(require_permission("tech_stack", "read")),
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    limit: int | None = None
) -> list[TechStackRead]:
    response: GetTechStackResponse = await handle_get_techstacks(db, current_user, page, limit)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@techstack_router.get("/{techstack_id}")
async def get_techstack_by_id(
    techstack_id: UUID,
    current_user: User = Depends(require_permission("tech_stack", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetTechStackResponse = await handle_get_techstack_by_id(db, current_user, techstack_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@techstack_router.post("/")
async def create_techstack(
    techstack: TechStackCreate,
    current_user: User = Depends(require_permission("tech_stack", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreateTechStackResponse = await handle_create_techstack(db, current_user, techstack)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=201,
    )


@techstack_router.put("/{techstack_id}")
async def update_techstack(
    techstack_id: UUID,
    techstack: TechStackUpdate,
    current_user: User = Depends(require_permission("tech_stack", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdateTechStackResponse = await handle_update_techstack(
        db, current_user, techstack, techstack_id
    )
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@techstack_router.delete("/{techstack_id}")
async def delete_techstack(
    techstack_id: UUID,
    current_user: User = Depends(require_permission("tech_stack", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeleteTechStackResponse = await handle_delete_techstack(db, current_user, techstack_id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
