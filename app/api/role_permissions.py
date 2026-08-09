from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.models.user import User
from app.responses.base import BaseResponse
from app.responses.role_permissions import (
    RolePermissionCreate,
    GetRolePermissionsResponse,
    GetRolePermissionResponse,
    CreateRolePermissionResponse,
    UpdateRolePermissionResponse,
)
from app.services.role_permissions import (
    get_all_role_permissions_service,
    get_role_permission_service,
    create_role_permission_service,
    update_role_permission_service,
    delete_role_permission_service,
)
from app.core.security import require_permission

router = APIRouter(prefix="/role-permissions", tags=["Role Permissions"])


@router.get("", response_model=GetRolePermissionsResponse)
async def get_role_permissions(
    current_user: User = Depends(require_permission("role_permissions", "read")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await get_all_role_permissions_service(db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )


@router.get("/{id}", response_model=GetRolePermissionResponse)
async def get_role_permission(
    id: UUID,
    current_user: User = Depends(require_permission("role_permissions", "read")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await get_role_permission_service(db, id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )


@router.post("", response_model=CreateRolePermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_role_permission(
    rp_data: RolePermissionCreate,
    current_user: User = Depends(require_permission("role_permissions", "create")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await create_role_permission_service(db, rp_data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response.model_dump(mode="json")
    )


@router.put("/{id}", response_model=UpdateRolePermissionResponse)
async def update_role_permission(
    id: UUID,
    rp_data: RolePermissionCreate,
    current_user: User = Depends(require_permission("role_permissions", "update")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await update_role_permission_service(db, id, rp_data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )


@router.delete("/{id}", response_model=BaseResponse)
async def delete_role_permission(
    id: UUID,
    current_user: User = Depends(require_permission("role_permissions", "delete")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await delete_role_permission_service(db, id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )
