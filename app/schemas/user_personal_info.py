from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.config import SortOrder, TimeRange
from app.schemas.common import TimeFilterOption
from app.schemas.password import Password

class UserPersonalInfoBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str | None = Field(None, max_length=100)
    date_of_birth: str = Field(..., description="Format: DD/MM/YYYY", json_schema_extra={"example": "03/09/2004"})
    primary_role_id: UUID = Field(...)
    branch_id: UUID | None = Field(None)
    highest_qualification: str = Field(..., max_length=100)
    specialization: str = Field(..., max_length=100)
    year_of_passout: int = Field(...)
    working_status_id: UUID = Field(...)

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
    primary_role_id: UUID | None = Field(None)
    branch_id: UUID | None = Field(None)
    highest_qualification: str | None = Field(None, max_length=100)
    specialization: str | None = Field(None, max_length=100)
    year_of_passout: int | None = Field(None)
    working_status_id: UUID | None = Field(None)

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


class UserPersonalInfoStatusUpdate(BaseModel):
    working_status_id: UUID


class UserPersonalInfoResponse(UserPersonalInfoBase):
    id: UUID
    user_id: UUID
    createdAt: datetime
    updatedAt: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserPersonalInfoFilterRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    time_filter: TimeRange | None = None
    sort_by: str | None = None
    order_by: SortOrder | None = None
    # Off by default so the response shape only widens when the caller asks for it.
    is_reporting_to: bool = False
    search: str | None = None
    # Every entity filter takes ids, never display names. Names are not unique (two job roles
    # differing only in case, two people sharing a full name), they change under a rename, and
    # `users.fullName` is not even a column. Ids also mean each filter reads a column on
    # user_personal_info itself rather than depending on a join. `year_of_passout` stays a
    # plain value - it names no row. Send what GET /user-personal-info/filters returns as `id`.
    primary_role: list[UUID] | None = None
    working_status: list[UUID] | None = None
    year_of_passout: list[int] | None = None
    team: list[UUID] | None = None
    branch: list[UUID] | None = None
    # Filters on `users.reporting_to` directly, so it needs none of the joins `is_reporting_to`
    # adds and works whether or not the reporting columns were asked for.
    reporting_to: list[UUID] | None = None
    # Free calendar window. Takes precedence over `time_filter` when both are sent.
    from_date: date | None = None
    to_date: date | None = None

    @model_validator(mode="after")
    def check_date_range(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValueError("to_date must be on or after from_date")
        return self

class UserManagementFilterRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    time_filter: TimeRange | None = None
    sort_by: str | None = None
    order_by: SortOrder | None = None
    search: str | None = None
    role_id: UUID | None = None
    # Free calendar window. Takes precedence over `time_filter` when both are sent.
    from_date: date | None = None
    to_date: date | None = None

    @model_validator(mode="after")
    def check_date_range(self):
        if self.from_date and self.to_date and self.to_date < self.from_date:
            raise ValueError("to_date must be on or after from_date")
        return self

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
    branch_name: str | None = None
    profiles_count: int
    # Populated only when is_reporting_to is requested. The route serialises with
    # exclude_unset, so these stay absent from the payload otherwise rather than
    # appearing as nulls.
    reporting_to_id: UUID | None = None
    reporting_to_name: str | None = None

class UserPersonalInfoPaginatedResponse(BaseModel):
    items: list[UserPersonalInfoListRead]
    total: int
    page: int
    limit: int
    total_pages: int


class FilterOption(BaseModel):
    """One selectable value. `id` is what the filter takes, `name` is what the dropdown shows."""

    id: UUID
    name: str


class UserProfileFiltersResponse(BaseModel):
    user_status: list[FilterOption]
    primary_role: list[FilterOption]
    # Not an entity, so it stays a bare value - the filter takes the year itself.
    year_of_passout: list[int]
    team: list[FilterOption]
    branch: list[FilterOption]
    reporting_to: list[FilterOption]
    time_filter: list[TimeFilterOption]

class UserPasswordUpdate(BaseModel):
    existing_password: str
    new_password: Password
    confirm_password: str