from uuid import UUID
from pydantic import BaseModel, Field

class UserManagementListRead(BaseModel):
    user_id: UUID
    full_name: str
    email: str
    role_name: str

class UserManagementPaginatedResponse(BaseModel):
    items: list[UserManagementListRead]
    total: int
    page: int
    limit: int
    total_pages: int
