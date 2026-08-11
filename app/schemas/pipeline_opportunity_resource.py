from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PipelineOpportunityResourceBase(BaseModel):
    opportunity_id: UUID = Field(..., description="Opportunity ID")
    user_id: UUID = Field(..., description="User ID")
    email: str = Field(..., min_length=1, max_length=255)
    variant_id: UUID = Field(..., description="Variant ID")
    variant_title: str = Field(..., min_length=1, max_length=255)
    experience_years: float = Field(...)
    match_percentage: float = Field(...)
    matching_skills: list[str] = Field(...)
    missing_skills: list[str] = Field(...)
    justification: str = Field(..., max_length=1000)
    is_active: bool = Field(True)


class PipelineOpportunityResourceDTO(PipelineOpportunityResourceBase):
    id: UUID = Field(..., description="Pipeline Opportunity Resource ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    createdBy: Optional[UUID] = Field(None)
    updatedBy: Optional[UUID] = Field(None)
    resourceApprovedBy: Optional[str] = Field(
        None, description="The person who approved the resource"
    )
    is_selected: Optional[bool] = Field(None)
    is_approved: Optional[bool] = Field(None)
    approved_at: Optional[datetime] = Field(None)
    approved_by: Optional[UUID] = Field(None)
    workingStatus: Optional[str] = Field(None)
    workingStatus: Optional[str] = Field(None)
    primaryJobRole: Optional[str] = Field(None)
    reportingTo: Optional[str] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class PipelineOpportunityResourceCreate(PipelineOpportunityResourceBase):
    pass


class PipelineOpportunityResourceUpdate(PipelineOpportunityResourceBase):
    opportunity_id: Optional[UUID] = Field(None)
    user_id: Optional[UUID] = Field(None)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    variant_id: Optional[UUID] = Field(None)
    variant_title: Optional[str] = Field(None, min_length=1, max_length=255)
    experience_years: Optional[float] = Field(None)
    match_percentage: Optional[float] = Field(None)
    matching_skills: Optional[list[str]] = Field(None)
    missing_skills: Optional[list[str]] = Field(None)
    justification: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = Field(None)


class PipelineOpportunityResourceSelectRequest(BaseModel):
    pipeline_resource_id: UUID = Field(..., description="Pipeline Opportunity Resource ID")
    is_selected: bool = Field(..., description="Is Selected")

