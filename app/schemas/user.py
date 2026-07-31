from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    fullName: str = Field(..., max_length=100)
    email: EmailStr = Field(..., max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserRead(UserBase):
    user_id: UUID
    refUID: str | None = None
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)

class UserHierarchy(BaseModel):
    user_id: UUID
    fullName: str
    children: list["UserHierarchy"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

UserHierarchy.model_rebuild()

    