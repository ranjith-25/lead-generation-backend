from pydantic import BaseModel,Field
from typing import Optional

class ProjectDomainBase(BaseModel):
    domain: str = Field(..., min_length=1, max_length=100)
    description: str  = Field(..., max_length=255)
    is_active: bool = Field(True)

class ProjectDomainDTO(ProjectDomainBase):
    id: int = Field(...,description="Project Domain ID")

class ProjectDomainCreate(ProjectDomainBase):
    pass


class ProjectDomainUpdate(ProjectDomainBase):
    domain : Optional[str]  = Field(None, min_length=1, max_length=100)
    description : Optional[str]  = Field(None, max_length=255)
    is_active : Optional[bool] = Field(None)