from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class PermissionBase(BaseModel):
    permission_key: str = Field(..., min_length=1, max_length=50, description="Permission Key")
    description: str = Field(..., max_length=100, description="Permission Description")
    display_name: str = Field(..., max_length=100, description="Display Name")


class PermissionDTO(PermissionBase):
    permission_id: UUID = Field(..., description="Permission ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    permission_key: Optional[str] = Field(None, min_length=1, max_length=50, description="Permission Key")
    description: Optional[str] = Field(None, max_length=100, description="Permission Description")
    display_name: Optional[str] = Field(None, max_length=100, description="Display Name")
