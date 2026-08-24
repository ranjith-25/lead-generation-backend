from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    roleName: str = Field(..., max_length=50)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    roleName: str | None = Field(None, max_length=50)


class RoleRead(RoleBase):
    role_id: UUID
    # Read-only. Absent from RoleCreate/RoleUpdate on purpose - a key identifies a row the
    # code addresses, so it is set by migration or seed, never through the API.
    role_key: str | None = None
    is_legacy_role: bool
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)
