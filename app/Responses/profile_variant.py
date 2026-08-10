from pydantic import BaseModel, Field
from app.responses.base import BaseResponse
from app.schemas.profile_variant import ProfileVariantDTO
from typing import List

class GetProfileVariantResponse(BaseResponse):
    profileVariantList: list[ProfileVariantDTO] | None = Field(default=None, description="List of Profile Variants")
    profileVariant: ProfileVariantDTO | None = Field(default=None, description="Profile Variant Details")


class CreateProfileVariantResponse(BaseResponse):
    newProfileVariant: ProfileVariantDTO | None = Field(default=None, description="Newly created Profile Variant")


class UpdateProfileVariantResponse(BaseResponse):
    updatedProfileVariant: ProfileVariantDTO | None = Field(default=None, description="Updated Profile Variant details")


class DeleteProfileVariantResponse(BaseResponse):
    pass


class RoleItem(BaseModel):
    job_role_name: str = Field(..., description="Job Role Name")
    job_role_id: str = Field(..., description="Job Role ID")

class JobRoleSkillsData(BaseModel):
    role: List[RoleItem] = Field(..., description="List of Job Roles")
    highlighted_skills: List[str] = Field(..., description="List of Tech Stack Names")

class JobRoleSkillsResponse(BaseResponse):
    status: bool = Field(True, description="Success Status")
    data: JobRoleSkillsData = Field(..., description="Job Roles and Skills Data")