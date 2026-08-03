from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserPersonalInfoBase(BaseModel):
    work_email: EmailStr = Field(..., max_length=100)
    date_of_birth: str = Field(..., description="Format: DD/MM/YYYY", json_schema_extra={"example": "03/09/2004"})
    primary_role: str = Field(..., max_length=100)
    branch: str = Field(..., max_length=100)
    highest_qualification: str = Field(..., max_length=100)
    specialization: str = Field(..., max_length=100)
    year_of_passout: int = Field(...)
    working_status: str = Field(..., max_length=50)

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: str) -> str:
        parts = v.split("/")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError("date_of_birth must be in DD/MM/YYYY format")
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            raise ValueError("date_of_birth contains invalid date numbers")
        return v


class UserPersonalInfoCreate(UserPersonalInfoBase):
    user_id: UUID


class UserPersonalInfoUpdate(BaseModel):
    work_email: EmailStr | None = Field(None, max_length=100)
    date_of_birth: str | None = Field(None, description="Format: DD/MM/YYYY")
    primary_role: str | None = Field(None, max_length=100)
    branch: str | None = Field(None, max_length=100)
    highest_qualification: str | None = Field(None, max_length=100)
    specialization: str | None = Field(None, max_length=100)
    year_of_passout: int | None = Field(None)
    working_status: str | None = Field(None, max_length=50)

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: str | None) -> str | None:
        if v is None:
            return v
        parts = v.split("/")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError("date_of_birth must be in DD/MM/YYYY format")
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            raise ValueError("date_of_birth contains invalid date numbers")
        return v


class UserPersonalInfoResponse(UserPersonalInfoBase):
    id: UUID
    user_id: UUID
    createdAt: datetime
    updatedAt: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
