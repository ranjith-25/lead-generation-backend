from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from uuid import UUID

class ProjectDomainBase(BaseModel):
    domain: str = Field(..., min_length=1, max_length=100)
    description: str  = Field(..., max_length=255)
    is_active: bool = Field(True)

class ProjectDomainDTO(ProjectDomainBase):
    id: UUID = Field(...,description="Project Domain ID")
    count : int = Field(0)
    model_config = ConfigDict(from_attributes=True)

class ProjectDomainCreate(ProjectDomainBase):
    pass


class ProjectDomainUpdate(ProjectDomainBase):
    domain : Optional[str]  = Field(None, min_length=1, max_length=100)
    description : Optional[str]  = Field(None, max_length=255)
    is_active : Optional[bool] = Field(None)
    
class ProjectDomainRead(ProjectDomainBase):
    id: UUID = Field(..., description="Project Domain ID")
    count : int = Field(0)
    model_config = ConfigDict(from_attributes=True)
    
class ProjectDomainFilters(BaseModel):
    search: str | None = None
    page: int | None = None
    limit: int | None = None