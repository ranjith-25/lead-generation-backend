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
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)
