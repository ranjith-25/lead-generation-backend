from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class SalesEnablementBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    opportunityID: UUID
    suggested_questions: list[str] | None = None
    sales_talking_points: list[str] | None = None
    outreach_template: str | None = None
    outreach_subject: str | None = None

class SalesEnablementCreate(SalesEnablementBase):
    pass

class SalesEnablementRead(SalesEnablementBase):
    id: UUID
    createdBy: UUID
    updatedBy: UUID
    createdAt: datetime
    updatedAt: datetime | None = None

class SalesEnablementUpdate(BaseModel):
    suggested_questions: list[str] | None = None
    sales_talking_points: list[str] | None = None
    outreach_template: str | None = None
    outreach_subject: str | None = None

class OutreachTemplateUpdate(BaseModel):
    outreach_template: str
    # Optional so the existing template-only payload still validates; the service sends
    # only the fields the client actually set.
    outreach_subject: str | None = None
