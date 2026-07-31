from pydantic import BaseModel, Field
from app.responses.base import BaseResponse
from app.schemas.auth import Token
from app.schemas.user import UserHierarchy
class AuthenticationResponse(BaseResponse,Token):
    user_id : str = Field(...,description="Logged in userID for the user")
    fullName : str = Field(...,description="Display name for the user")
    role : str = Field(...,description="Role Name for the user")
    permissions : list[str] = Field(...,description="Roles allowed permission for the user")

class HierarchyResponse(BaseResponse):
    hierarchy : UserHierarchy