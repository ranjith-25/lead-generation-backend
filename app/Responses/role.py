from pydantic import BaseModel, Field

from app.responses.base import BaseResponse
from app.schemas.role import RoleRead


class GetRoleResponse(BaseResponse):
    role: RoleRead | None = Field(default=None, description="Role details")


class CreateRoleResponse(BaseResponse):
    role: RoleRead | None = Field(default=None, description="Newly created Role")


class UpdateRoleResponse(BaseResponse):
    role: RoleRead | None = Field(default=None, description="Updated Role details")


class DeleteRoleResponse(BaseResponse):
    pass
