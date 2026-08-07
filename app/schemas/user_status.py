from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class UserStatusBase(BaseModel):
    displayName: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(True)


class UserStatusDTO(UserStatusBase):
    id: int = Field(..., description="User Status ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    createdBy: Optional[uuid.UUID] = Field(None)
    updatedBy: Optional[uuid.UUID] = Field(None)
    model_config = ConfigDict(from_attributes=True)


class UserStatusCreate(UserStatusBase):
    pass


class UserStatusUpdate(UserStatusBase):
    displayName: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(None)

class UserStatusListRead(BaseModel):
    id: int
    status: str
    count: int

    model_config = ConfigDict(from_attributes=True)
