from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ProfileVariantProjectBase(BaseModel):
    project_id: uuid.UUID
    project_name: str = Field(..., min_length=1, max_length=255)
    projectDomainID: uuid.UUID
    techstacks: List[str] = Field(..., description="List of tech stacks")
    description: str
    links: dict[str, str] = Field(default_factory=dict)


class ProfileVariantProjectDTO(ProfileVariantProjectBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileVariantProjectCreate(ProfileVariantProjectBase):
    pass


class ProfileVariantProjectUpdate(BaseModel):
    project_id: uuid.UUID
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    projectDomainID: Optional[uuid.UUID] = None
    techstacks: Optional[List[str]] = None
    description: Optional[str] = None
    links: Optional[dict[str, str]] = None


class ProfileVariantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: uuid.UUID = Field(..., description="Job Role ID")
    experience: str = Field(..., min_length=1, max_length=255)
    highlighted_skills: List[str] = Field(..., description="List of highlighted skills")
    upload_profile: str = Field(..., max_length=255)
    certificate: Optional[List[str]] = Field(None, description="List of certificates")
    is_draft: bool = Field(True)
    user_id: uuid.UUID = Field(..., description="Associated User ID")


class ProfileVariantDTO(ProfileVariantBase):
    profile_variant_id: uuid.UUID
    created_by: uuid.UUID
    updated_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    projects: List[ProfileVariantProjectDTO] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProfileVariantCreate(ProfileVariantBase):
    projects: List[ProfileVariantProjectCreate] = Field(default_factory=list)


class ProfileVariantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[uuid.UUID] = Field(None, description="Job Role ID")
    experience: Optional[str] = Field(None, min_length=1, max_length=255)
    highlighted_skills: Optional[List[str]] = Field(None, description="List of highlighted skills")
    upload_profile: Optional[str] = Field(None, max_length=255)
    certificate: Optional[List[str]] = Field(None, description="List of certificates")
    is_draft: Optional[bool] = Field(None)
    user_id: Optional[uuid.UUID] = Field(None, description="Associated User ID")
    projects: Optional[List[ProfileVariantProjectUpdate]] = Field(None)