from pydantic import BaseModel

from app.schemas.system_log import SystemLogRead


class SystemLogPaginatedResponse(BaseModel):
    data: list[SystemLogRead]
    total: int
    page: int
    size: int
    total_pages: int
