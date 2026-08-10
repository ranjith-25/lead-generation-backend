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

class UserHierarchy(BaseModel):
    user_id: UUID
    fullName: str
    specialization : str | None = None
    roleName : str 
    children: list["UserHierarchy"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

UserHierarchy.model_rebuild()


class UserRegistrationFromInvitation(BaseModel):
    user_details : UserCreate
    user_personal_details : UserPersonalInfoCreate
    
    