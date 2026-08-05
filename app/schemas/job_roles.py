from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class JobRolesBase(BaseModel):
    
    displayName: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(True)


class JobRolesDTO(JobRolesBase):
    id: int = Field(..., description="Job Role ID")
    normalizedName: str = Field(..., min_length=1, max_length=100)
    model_config = ConfigDict(from_attributes=True)


class JobRolesCreate(JobRolesBase):
    
    pass


class JobRolesUpdate(JobRolesBase):
    displayName: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(None)
