from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.config import EditChangeType, PageName


class OpportunityEditChangeRead(BaseModel):
    """One field's change, already resolved for display.

    `old`/`new` are the readable forms, not the raw stored values — an id field reads as the
    name it points at, a list as a comma-joined string, and anything with no readable inline
    form (JSON blobs, ids whose row is gone) is null with the sentence falling back to its
    value-free wording.
    """

    model_config = ConfigDict(from_attributes=True)

    field: str = Field(..., description="The opportunity column that changed")
    label: str = Field(..., description="Human label for the column, e.g. 'Job Description'")
    change_type: EditChangeType
    old: str | None = Field(None, description="Previous value, readable; null when it had none")
    new: str | None = Field(None, description="New value, readable; null when it was cleared")
    sentence: str = Field(..., description="Ready-to-render sentence for this one field")


class OpportunityEditHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    opportunity_id: UUID
    page_name: PageName
    edited_by: UUID | None = None
    edited_by_name: str
    edited_at: str
    sentence: str = Field(..., description="One sentence covering the whole edit")
    changes: list[OpportunityEditChangeRead] = Field(
        default_factory=list, description="Per-field sentences, ordered as stored"
    )


class OpportunityEditHistoryPaginatedResponse(BaseModel):
    data: list[OpportunityEditHistoryRead]
    total: int
    page: int
    size: int
    total_pages: int
