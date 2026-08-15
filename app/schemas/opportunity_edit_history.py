from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.config import PageName


class OpportunityEditChange(BaseModel):
    """The before/after of one field in a single edit."""

    model_config = ConfigDict(from_attributes=True)
    old: Any = None
    new: Any = None


class OpportunityEditHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    opportunity_id: UUID
    page_name: PageName
    edited_by: UUID | None = None
    edited_by_name: str
    edited_fields: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("editedFields", "edited_fields"),
    )
    changes: dict[str, OpportunityEditChange]
    edited_at: datetime


class OpportunityEditHistoryPaginatedResponse(BaseModel):
    data: list[OpportunityEditHistoryRead]
    total: int
    page: int
    size: int
    total_pages: int
