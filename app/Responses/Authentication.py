from pydantic import BaseModel, Field
from app.Responses.Base import BaseResponse
from app.schemas.auth import Token
class AuthenticationResponse(BaseResponse,Token):
    user_id : str = Field(...,description="Logged in userID for the user")
    fullName : str = Field(...,description="Display name for the user")
    role : str = Field(...,description="Role Name for the user")
    permissions : list[str] = Field(...,description="Roles allowed permission for the user")
