from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PipelineOpportunityProjectBase(BaseModel):
    opportunity_id: UUID = Field(..., description="Opportunity ID")
    project_id: UUID = Field(..., description="Project ID")
    project_name: str = Field(..., min_length=1, max_length=255)
    match_score: float = Field(...)
    justification: str = Field(..., max_length=500)
    matched_evidence: list[str] = Field(...)
    is_active: bool = Field(True)


class PipelineOpportunityProjectDTO(PipelineOpportunityProjectBase):
    id: UUID = Field(..., description="Pipeline Opportunity Project ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    createdBy: Optional[UUID] = Field(None)
    updatedBy: Optional[UUID] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class PipelineOpportunityProjectCreate(PipelineOpportunityProjectBase):
    pass


class PipelineOpportunityProjectUpdate(PipelineOpportunityProjectBase):
    opportunity_id: Optional[UUID] = Field(None)
    project_id: Optional[UUID] = Field(None)
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    match_score: Optional[float] = Field(None)
    justification: Optional[str] = Field(None, max_length=500)
    matched_evidence: Optional[list[str]] = Field(None)
    is_active: Optional[bool] = Field(None)
