from typing import Optional
from pydantic import Field

from app.responses.base import BaseResponse
from app.schemas.pipeline_opportunity_techincal_preperation import PipelineOpportunityTechnicalPreperationDTO


class GetPipelineOpportunityTechnicalPreperationResponse(BaseResponse):
    pipelineOpportunityTechnicalPreperation: Optional[PipelineOpportunityTechnicalPreperationDTO] = Field(None, description="Pipeline Opportunity Technical Preperation")
    pipelineOpportunityTechnicalPreperationList: Optional[list[PipelineOpportunityTechnicalPreperationDTO]] = Field(None, description="Pipeline Opportunity Technical Preperation List")
    total: int = Field(0)
    page: int = Field(1)
    limit: int = Field(10)
    total_pages: int = Field(1)
    status_code: int = Field(200)


class CreatePipelineOpportunityTechnicalPreperationResponse(BaseResponse):
    newPipelineOpportunityTechnicalPreperation: PipelineOpportunityTechnicalPreperationDTO = Field(..., description="New Pipeline Opportunity Technical Preperation Created")
    status_code: int = Field(200)


class UpdatePipelineOpportunityTechnicalPreperationResponse(BaseResponse):
    updatedPipelineOpportunityTechnicalPreperation: PipelineOpportunityTechnicalPreperationDTO = Field(..., description="Pipeline Opportunity Technical Preperation Updated")
    status_code: int = Field(200)


class DeletePipelineOpportunityTechnicalPreperationResponse(BaseResponse):
    status_code: int = Field(200)
