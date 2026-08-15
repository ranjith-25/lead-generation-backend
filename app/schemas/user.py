from __future__ import annotations
from datetime import datetime
from uuid import UUID
from app.schemas.password import Password
from app.schemas.user_personal_info import UserPersonalInfoCreate
from pydantic import BaseModel, ConfigDict, EmailStr, Field,model_validator


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=100)


class UserCreate(UserBase):
    password: Password
    confirmPassword: str

    @model_validator(mode="after")
    def checkPasswords(self):
        if self.password != self.confirmPassword:
            raise ValueError("Password and Confirm password must match")
        return self


class UserRead(UserBase):
    user_id: UUID
    fullName: str
    refUID: str | None = None
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)

class UserRoleRead(BaseModel):
    user_id: UUID
    full_name: str
    email: EmailStr
    role_id: UUID | None = None
    role_name: str | None = None
    reporting_to: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserHierarchy(BaseModel):
    user_id: UUID
    fullName: str
    working_status : str | None = None
    roleName : str | None = None
    children: list["UserHierarchy"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

UserHierarchy.model_rebuild()


class UserRegistrationFromInvitation(BaseModel):
    user_details : UserCreate
    user_personal_details : UserPersonalInfoCreate
    
class UserReportingRead(UserRead):
    reporting_to: UUID


class UserRoleChangeUser(BaseModel):
    user_id: UUID
    email: str
    fullName: str

    model_config = ConfigDict(from_attributes=True)


class UserRoleChangeResult(BaseModel):
    """Outcome of a bulk role move — `users` lists who was on the source role before it ran."""

    current_role: str
    current_role_id: UUID
    destination_role: str
    destination_role_id: UUID
    changed_count: int
    dry_run: bool = False
    users: list[UserRoleChangeUser] = Field(default_factory=list)