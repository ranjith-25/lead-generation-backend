from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import require_permission
from app.models.user import User
from app.responses.platform import (
    CreatePlatformResponse,
    DeletePlatformResponse,
    GetPlatformResponse,
    UpdatePlatformResponse,
)
from app.schemas.platform import PlatformCreate, PlatformUpdate
from app.services.platform import (
    handle_create_platform,
    handle_delete_platform,
    handle_get_all_platforms,
    handle_get_platform_by_id,
    handle_update_platform,
)

platform_router = APIRouter(prefix="/platform", tags=["Platform"])


@platform_router.get("/")
async def get_all_platforms(
    current_user: User = Depends(require_permission("platform", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPlatformResponse = await handle_get_all_platforms(db, current_user)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@platform_router.get("/{id}")
async def get_platform_by_id(
    id: int,
    current_user: User = Depends(require_permission("platform", "read")),
    db: AsyncSession = Depends(get_db),
):
    response: GetPlatformResponse = await handle_get_platform_by_id(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@platform_router.post("/")
async def create_platform(
    platform: PlatformCreate,
    current_user: User = Depends(require_permission("platform", "create")),
    db: AsyncSession = Depends(get_db),
):
    response: CreatePlatformResponse = await handle_create_platform(db, current_user, platform)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@platform_router.put("/{id}")
async def update_platform(
    id: int,
    platform: PlatformUpdate,
    current_user: User = Depends(require_permission("platform", "update")),
    db: AsyncSession = Depends(get_db),
):
    response: UpdatePlatformResponse = await handle_update_platform(db, current_user, platform, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )


@platform_router.delete("/{id}")
async def delete_platform(
    id: int,
    current_user: User = Depends(require_permission("platform", "delete")),
    db: AsyncSession = Depends(get_db),
):
    response: DeletePlatformResponse = await handle_delete_platform(db, current_user, id)
    return JSONResponse(
        content=response.model_dump(mode="json", exclude_none=True),
        status_code=200,
    )
