from datetime import datetime
from enum import Enum
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class InvitationStatus(str, Enum):
    PENDING = "pending"
    REGISTERED = "registered"
    CANCELLED = "cancelled"


class UserInvitationBase(BaseModel):
    work_email: str = Field(..., min_length=1, max_length=100)
    roleID: int = Field(..., description="Role ID")
    reporting_to: uuid.UUID = Field(..., description="Reporting To User ID")
    status: InvitationStatus = Field(InvitationStatus.PENDING)
    user_id: Optional[uuid.UUID] = Field(None)
    is_deleted: bool = Field(False)

class UserInvitationDTO(UserInvitationBase):
    id: uuid.UUID = Field(..., description="User Invitation ID")

    model_config = ConfigDict(from_attributes=True)


class UserInvitationCreate(UserInvitationBase):
    pass


class UserInvitationUpdate(BaseModel):
    status: Optional[InvitationStatus] = Field(None)


class UserInvitationRead(UserInvitationBase):
    id: uuid.UUID = Field(..., description="User Invitation ID")
    createdAt: Optional[datetime] = Field(None)
    updatedAt: Optional[datetime] = Field(None)
    invitedBy: Optional[uuid.UUID] = Field(None)
    updatedBy: Optional[uuid.UUID] = Field(None)

    model_config = ConfigDict(from_attributes=True)