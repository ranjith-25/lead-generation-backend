from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class ApprovalStatus(str, Enum):
    SELECTED = "SELECTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUGGESTED = "SUGGESTED"
    ASSIGNED_TO_TL = "ASSIGNED_TO_TL" 


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
    status: ApprovalStatus = Field(..., description="Approval status of the resource")
    is_auto_approved: Optional[bool] = Field(
        None,
        description="True when the resource was approved automatically by a user holding the auto approve permission",
    )
    approved_at: Optional[datetime] = Field(None)
    resourceApprovedBy: Optional[str] = Field(None)
    rejected_at: Optional[datetime] = Field(None)
    resourceRejectedBy: Optional[str] = Field(None)
    reject_reason: Optional[str] = Field(None)
    resourceAssignedToTLBy: Optional[str] = Field(
        None, description="The person who assigned the resource to the TL"
    )
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
    pipeline_resource_id_list: list[UUID] = Field(..., description="Pipeline Opportunity Resource ID list")


class PipelineOpportunityResourceAssignToTLRequest(BaseModel):
    pipeline_resource_id: UUID = Field(..., description="Pipeline Opportunity Resource ID")


class PipelineOpportunityResourceApproveRequest(BaseModel):
    pipeline_resource_id: UUID = Field(..., description="Pipeline Opportunity Resource ID")


class PipelineOpportunityResourceAutoApproveRequest(BaseModel):
    pipeline_resource_id: UUID = Field(..., description="Pipeline Opportunity Resource ID")


class PipelineOpportunityResourceRejectRequest(BaseModel):
    pipeline_resource_id: UUID = Field(..., description="Pipeline Opportunity Resource ID")
    reject_reason: str = Field(..., min_length=1, max_length=1000, description="Reason for rejection")
