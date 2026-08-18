from app.responses.base import BaseResponse
from app.schemas.common import TimeFilterOption
from app.schemas.project import ProjectRead
from dataclasses import dataclass
from typing import BinaryIO
class ProjectListResponse(BaseResponse):
    total: int
    page: int
    limit: int
    projects: list[ProjectRead] = []

class ProjectFilterResponse(BaseResponse):
    Domains: list[str]
    Techstack: list[str]
    time_filter: list[TimeFilterOption]

class CreateProjectResponse(BaseResponse):
    project: ProjectRead
    ai_ingest_failed: bool = False
    ai_error: str | None = None

@dataclass
class FileDownloadResponse:
    file_stream: BinaryIO
    file_name: str
    content_type: str