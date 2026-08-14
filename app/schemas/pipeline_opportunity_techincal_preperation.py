from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PipelineOpportunityTechnicalPreperationBase(BaseModel):
    opportunity_id: UUID = Field(..., description="Opportunity ID")
    candidate_name: Optional[str] = Field(None, max_length=255)
    variant_title: Optional[str] = Field(None,  max_length=255)
    technical_briefing_note: Optional[str] = Field(None, max_length=1000)
    interview_preparation_guide: Optional[list[dict]] = Field(None)
    comments : Optional[list[str]]  = Field(None)
    is_active: bool = Field(True)


class PipelineOpportunityTechnicalPreperationDTO(PipelineOpportunityTechnicalPreperationBase):
    id: UUID = Field(..., description="Pipeline Opportunity Technical Preperation ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    createdBy: Optional[UUID] = Field(None)
    updatedBy: Optional[UUID] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class PipelineOpportunityTechnicalPreperationCreate(PipelineOpportunityTechnicalPreperationBase):
    pass


class PipelineOpportunityTechnicalPreperationUpdate(BaseModel):
    opportunity_id: Optional[UUID] = Field(None)
    user_id: Optional[UUID] = Field(None)
    candidate_name: Optional[str] = Field(None, min_length=1, max_length=255)
    variant_title: Optional[str] = Field(None, min_length=1, max_length=255)
    technical_briefing_note: Optional[str] = Field(None, max_length=1000)
    interview_preparation_guide: Optional[list[dict]] = Field(None)
    is_active: Optional[bool] = Field(None)
