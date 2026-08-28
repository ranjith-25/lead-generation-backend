from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SpecializationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class SpecializationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)


class SpecializationOut(BaseModel):
    specialization_id: UUID
    name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)