from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserPersonalInfoBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str | None = Field(None, max_length=100)
    date_of_birth: str = Field(..., description="Format: DD/MM/YYYY", json_schema_extra={"example": "03/09/2004"})
    primary_role_id: int = Field(...)
    branch_id: int | None = Field(None)
    highest_qualification: str = Field(..., max_length=100)
    specialization: str = Field(..., max_length=100)
    year_of_passout: int = Field(...)
    working_status_id: int = Field(...)

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
    pass


class UserPersonalInfoUpdate(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    date_of_birth: str | None = Field(None, description="Format: DD/MM/YYYY")
    primary_role_id: int | None = Field(None)
    branch_id: int | None = Field(None)
    highest_qualification: str | None = Field(None, max_length=100)
    specialization: str | None = Field(None, max_length=100)
    year_of_passout: int | None = Field(None)
    working_status_id: int | None = Field(None)

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
    id: int
    user_id: UUID
    createdAt: datetime
    updatedAt: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserPersonalInfoFilterRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: str | None = None
    primary_role_id: int | None = None
    working_status_id: int | None = None
    year_of_passout: int | None = None

class UserManagementFilterRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    search: str | None = None
    role_id: int | None = None

class UserPersonalInfoListRead(BaseModel):
    user_id: UUID
    email: str
    first_name: str
    last_name: str | None
    primary_role_name: str
    date_of_birth: str
    highest_qualification: str
    year_of_passout: int
    working_status_name: str
    profiles_count: int

class UserPersonalInfoPaginatedResponse(BaseModel):
    items: list[UserPersonalInfoListRead]
    total: int
    page: int
    limit: int
    total_pages: int


class FilterItem(BaseModel):
    id: int
    name: str

class UserProfileFiltersResponse(BaseModel):
    user_status: list[FilterItem]
    primary_role: list[FilterItem]
    year_of_passout: list[int]

