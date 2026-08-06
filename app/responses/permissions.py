from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.permissions import PermissionDTO
from app.responses.base import BaseResponse


class GetPermissionResponse(BaseResponse):
    permission: Optional[PermissionDTO] = Field(None, description="Permission")
    permissionList: Optional[list[PermissionDTO]] = Field(None, description="Permission List")
    status_code: Optional[int] = Field(None, description="Status code")


class CreatePermissionResponse(BaseResponse):
    newPermission: Optional[PermissionDTO] = Field(None, description="New Permission Created")
    status_code: Optional[int] = Field(None, description="Status code")


class UpdatePermissionResponse(BaseResponse):
    updatedPermission: Optional[PermissionDTO] = Field(None, description="Permission Updated")
    status_code: Optional[int] = Field(None, description="Status code")


class DeletePermissionResponse(BaseResponse):
    status_code: Optional[int] = Field(None, description="Status code")
