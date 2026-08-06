from app.responses.base import BaseResponse
from app.schemas.project_domains import ProjectDomainRead

class DomainsListResponse(BaseResponse):
    total: int
    page: int
    limit: int
    projects: list[ProjectDomainRead] = []