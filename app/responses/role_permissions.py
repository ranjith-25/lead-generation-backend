from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.responses.base import BaseResponse

class RolePermissionBase(BaseModel):
    role_id: int
    feature_id: int
    permission_id: int

    model_config = ConfigDict(from_attributes=True)

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionRead(RolePermissionBase):
    role_permission_id: int
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
