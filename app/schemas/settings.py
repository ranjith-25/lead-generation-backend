from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeaturePermissionRead(BaseModel):
    """One permission, plus whether the role being inspected currently holds it."""

    permissionID: UUID
    permissionKey: str
    permissionName: str
    assigned: bool

    model_config = ConfigDict(from_attributes=True)


class FeaturePermissionsRead(BaseModel):

    featureID: UUID
    featureName: str
    featureKey: str
    permissions: list[FeaturePermissionRead]

    model_config = ConfigDict(from_attributes=True)


FeaturePermissionsRead.model_rebuild()


class RolePermissionMatrixRead(BaseModel):
    roleID: UUID
    roleName: str
    features: list[FeaturePermissionsRead]

    model_config = ConfigDict(from_attributes=True)


class FeaturePermissionUpdate(BaseModel):
    permissionID: UUID
    assigned: bool


class FeaturePermissionsUpdate(BaseModel):
    """The toggles of a single feature row."""

    featureID: UUID
    permissions: list[FeaturePermissionUpdate]


class RolePermissionMatrixUpdate(BaseModel):
    features: list[FeaturePermissionsUpdate] = Field(min_length=1)
    