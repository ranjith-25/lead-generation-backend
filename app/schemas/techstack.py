from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class TechStackBase(BaseModel):
    techstack_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=255)
    is_active: bool = Field(True)


class TechStackDTO(TechStackBase):
    techstack_id: UUID = Field(..., description="Tech Stack ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    createdBy: Optional[UUID] = Field(None, description="User who added this tech stack")
    updatedBy: Optional[UUID] = Field(None, description="User who last changed it")

    model_config = ConfigDict(from_attributes=True)


class TechStackCreate(TechStackBase):
    pass


class TechStackUpdate(TechStackBase):
    techstack_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(None)


class TechStackRead(TechStackBase):
    techstack_id: UUID = Field(..., description="Tech Stack ID")

    model_config = ConfigDict(from_attributes=True)

class TechstackFilters(BaseModel):
    search: str | None = None
    page: int | None = None
    limit: int | None = None