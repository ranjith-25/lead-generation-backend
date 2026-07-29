import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SampleCreate(BaseModel):
    name: str
    description: str | None = None


class SampleRead(SampleCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None = None
