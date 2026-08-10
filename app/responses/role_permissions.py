from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.responses.base import BaseResponse

class RolePermissionBase(BaseModel):
    role_id: UUID
    feature_id: UUID
    permission_id: UUID

    model_config = ConfigDict(from_attributes=True)

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionRead(RolePermissionBase):
    role_permission_id: UUID
    isDeleted: bool
    created_at: datetime

class GetRolePermissionsResponse(BaseResponse):
    role_permissions: list[RolePermissionRead]

class GetRolePermissionResponse(BaseResponse):
    role_permission: RolePermissionRead

class CreateRolePermissionResponse(BaseResponse):
    role_permission: RolePermissionRead

class UpdateRolePermissionResponse(BaseResponse):
    role_permission: RolePermissionRead
