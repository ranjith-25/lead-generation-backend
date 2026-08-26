from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EducationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class EducationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)


class EducationOut(BaseModel):
    education_id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)