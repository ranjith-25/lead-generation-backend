from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PipelineExecutionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    @property
    def status_text(self) -> str:
        return {
            PipelineExecutionStatus.PENDING: "Execution not started yet.",
            PipelineExecutionStatus.COMPLETED: "Execution completed successfully.",
            PipelineExecutionStatus.FAILED: "Execution failed."
        }[self]


class PipelineExecutionStatusBase(BaseModel):
    projects: PipelineExecutionStatus = Field(default=PipelineExecutionStatus.PENDING)
    salesEnablement: PipelineExecutionStatus = Field(default=PipelineExecutionStatus.PENDING)
    resourceMatch: PipelineExecutionStatus = Field(default=PipelineExecutionStatus.PENDING)
    technicalPreperation: PipelineExecutionStatus = Field(default=PipelineExecutionStatus.PENDING)
    execution_message: Optional[str] = Field(None, max_length=255)
    opportunity_id: UUID = Field(..., description="Opportunity ID")
    is_active: bool = Field(True)


class PipelineExecutionStatusDTO(PipelineExecutionStatusBase):
    id: UUID = Field(..., description="Pipeline Execution Status ID")
    model_config = ConfigDict(from_attributes=True)


class PipelineExecutionStatusCreate(PipelineExecutionStatusBase):
    pass


class PipelineExecutionStatusUpdate(PipelineExecutionStatusBase):
    projects: Optional[PipelineExecutionStatus] = Field(None)
    salesEnablement: Optional[PipelineExecutionStatus] = Field(None)
    resourceMatch: Optional[PipelineExecutionStatus] = Field(None)
    technicalPreperation: Optional[PipelineExecutionStatus] = Field(None)
    execution_message: Optional[str] = Field(None, max_length=255)
    opportunity_id: Optional[UUID] = Field(None)
    is_active: Optional[bool] = Field(None)
