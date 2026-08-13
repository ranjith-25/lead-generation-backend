from app.responses.base import BaseResponse
from app.schemas.common import TimeFilterOption
from app.schemas.project import ProjectRead


class ProjectListResponse(BaseResponse):
    total: int
    page: int
    limit: int
    projects: list[ProjectRead] = []

class ProjectFilterResponse(BaseResponse):
    Domains: list[str]
    Techstack: list[str]
    time_filter: list[TimeFilterOption]