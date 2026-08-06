from app.responses.base import BaseResponse
from app.schemas.project import ProjectRead


class ProjectListResponse(BaseResponse):
    total: int
    page: int
    limit: int
    projects: list[ProjectRead] = []
