from uuid import UUID

from app.responses.base import BaseResponse
from app.schemas.settings import FeaturePermissionsRead


class GetRolePermissionMatrixResponse(BaseResponse):
    roleID: UUID
    roleName: str
    features: list[FeaturePermissionsRead]


class UpdateRolePermissionMatrixResponse(GetRolePermissionMatrixResponse):
    """The matrix re-read after the toggles were applied, so the screen can re-render from the
    server's state instead of its own optimistic one."""