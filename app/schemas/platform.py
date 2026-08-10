from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PlatformBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(True)


class PlatformDTO(PlatformBase):
    id: UUID = Field(..., description="Platform ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(PlatformBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(None)

class PlatformListRead(BaseModel):
    platform_id: UUID
    name: str
    is_account_linked: bool
    count: int

    model_config = ConfigDict(from_attributes=True)
