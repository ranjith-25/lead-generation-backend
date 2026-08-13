from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class UserProjectBase(BaseModel):
    project_id: UUID = Field(..., description="Project the user is allocated to")
    role_id: UUID = Field(..., description="Job role the user is allocated as")
    techstack_id: UUID = Field(..., description="Techstack the user is allocated for")
    user_id: UUID = Field(..., description="Allocated user")


class UserProjectDTO(UserProjectBase):
    user_project_id: UUID = Field(..., description="User Project ID")
    allocated_by: Optional[UUID] = Field(None, description="User who created the allocation")
    allocation_updated_by: Optional[UUID] = Field(None, description="User who last edited the allocation")
    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class UserProjectCreate(UserProjectBase):
    pass


class UserProjectFilter(BaseModel):
    user_id: Optional[UUID] = Field(None, description="Restrict the result to one user")


class UserProjectUpdate(BaseModel):
    project_id: Optional[UUID] = Field(None, description="Project the user is allocated to")
    role_id: Optional[UUID] = Field(None, description="Job role the user is allocated as")
    techstack_id: Optional[UUID] = Field(None, description="Techstack the user is allocated for")