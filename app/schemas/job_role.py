from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class JobRoleBase(BaseModel):
    roleName: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(True)


class JobRoleDTO(JobRoleBase):
    id: int = Field(..., description="Job Role ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    createdBy: Optional[uuid.UUID] = Field(None)
    updatedBy: Optional[uuid.UUID] = Field(None)
    model_config = ConfigDict(from_attributes=True)
    user_count : int = 0


class JobRoleCreate(JobRoleBase):
    pass


class JobRoleUpdate(BaseModel):
    roleName: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(None)

class JobRoleRead(JobRoleBase):
    user_count: int = 0
    
class JobRoleFilters(BaseModel):
    search: str | None = None
    page: int | None = None
    limit: int | None = None