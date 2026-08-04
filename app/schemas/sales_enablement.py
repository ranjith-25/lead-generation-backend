from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class SalesEnablementBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    opportunityID: int
    suggested_questions: list[str] | None = None
    sales_talking_points: list[str] | None = None
    outreach_template: str | None = None
    relevant_projects: list[dict] | None = None

class SalesEnablementCreate(SalesEnablementBase):
    pass

class SalesEnablementRead(SalesEnablementBase):
    id: int
    createdBy: UUID
    updatedBy: UUID
    createdAt: datetime
    updatedAt: datetime | None = None
