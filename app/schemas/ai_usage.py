from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)

# Parsing the timestamp through an adapter rather than letting the field do it is what
# lets an unreadable value fall back to None instead of failing the entry it sits on.
_TIMESTAMP_ADAPTER = TypeAdapter(datetime)


class AIUsageLogEntry(BaseModel):

    model_config = ConfigDict(extra="allow")

    timestamp: datetime | None = Field(None, description="When the AI call happened")
    user: str | None = Field(None, description="Who triggered the call")
    action: str | None = Field(
        None, description="What the AI was asked to do, e.g. SCRAPE_JOB"
    )
    module: str | None = Field(
        None, description="Which part of the product the call came from"
    )

    @model_validator(mode="before")
    @classmethod
    def _wrap_plain_line(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"raw": value}
        return value

    @field_validator("timestamp", mode="before")
    @classmethod
    def _parse_timestamp(cls, value: Any) -> datetime | None:
        if value is None or value == "":
            return None
        try:
            return _TIMESTAMP_ADAPTER.validate_python(value)
        except ValidationError:
            return None

    @field_validator("user", "action", "module", mode="before")
    @classmethod
    def _as_text(cls, value: Any) -> str | None:
        """Whatever the AI sent still reads as something on screen; blanks become null."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None
