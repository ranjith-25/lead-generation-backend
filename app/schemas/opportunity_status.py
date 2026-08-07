from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OpportunityStatusBase(BaseModel):
    status: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(True)


class OpportunityStatusDTO(OpportunityStatusBase):
    id: int = Field(..., description="Opportunity Status ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class OpportunityStatusCreate(OpportunityStatusBase):
    pass


class OpportunityStatusUpdate(OpportunityStatusBase):
    status: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(None)

class OpportunityStatusListRead(BaseModel):
    id: int
    status: str
    count: int

    model_config = ConfigDict(from_attributes=True)
