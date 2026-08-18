from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.config import LogAction, LogModule


class SystemLogRead(BaseModel):
    """The list row: timestamp / user / action / module, plus the stored sentence.

    `details` is deliberately absent — the log stores rich context but the fetch stays lean.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    timestamp: datetime = Field(..., description="When the action happened")
    performed_by: UUID | None = Field(None, description="Actor's user id, for filtering")
    performed_by_name: str = Field(..., description="Actor's name as it read at action time")
    action: LogAction
    action_label: str = Field(..., description="Display label for the action")
    module: LogModule
    module_label: str = Field(..., description="Display label for the module")
    description: str = Field(..., description="Pre-rendered sentence for the timeline")


class SystemLogDetailRead(SystemLogRead):
    """The detail row: everything the list returns plus the entity pointer and `details`."""

    entity_type: str | None = None
    entity_id: UUID | None = None
    details: dict[str, Any] | None = None


class SystemLogFilterRequest(BaseModel):
    module: LogModule | None = None
    action: LogAction | None = None
    performed_by: UUID | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    search: str | None = Field(
        None, description="Matches against description / performed_by_name"
    )
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
