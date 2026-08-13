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


class ProjectInfo(BaseModel):
    project_id: UUID = Field(..., description="Project ID")
    project_name: str = Field(..., description="Project Name")


class RoleInfo(BaseModel):
    role_id: UUID = Field(..., description="Job Role ID")
    role_name: str = Field(..., description="Job Role Name")


class TechStackInfo(BaseModel):
    techstack_id: UUID = Field(..., description="Techstack ID")
    techstack_name: str = Field(..., description="Techstack Name")


# read-side shape: the three lookup FKs are expanded into {id, name} objects so callers
# do not have to resolve them separately
class UserProjectDetailDTO(BaseModel):
    project: ProjectInfo = Field(..., description="Allocated project")
    role: RoleInfo = Field(..., description="Job role of the allocation")
    techstack: TechStackInfo = Field(..., description="Techstack of the allocation")
    user_id: UUID = Field(..., description="Allocated user")
    user_project_id: UUID = Field(..., description="User Project ID")
    allocated_by: Optional[UUID] = Field(None, description="User who created the allocation")
    allocation_updated_by: Optional[UUID] = Field(None, description="User who last edited the allocation")
    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)


class UserProjectFilter(BaseModel):
    user_id: Optional[UUID] = Field(None, description="Restrict the result to one user")


class UserProjectUpdate(BaseModel):
    project_id: Optional[UUID] = Field(None, description="Project the user is allocated to")
    role_id: Optional[UUID] = Field(None, description="Job role the user is allocated as")
    techstack_id: Optional[UUID] = Field(None, description="Techstack the user is allocated for")