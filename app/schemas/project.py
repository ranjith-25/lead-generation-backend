from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LinkBase(BaseModel):
    case_study: str | None = None
    app_link: str | None = None


class DomainRead(BaseModel):
    domain_id: int
    domain_name: str
    description: str | None = None


class TechStackRead(BaseModel):
    techstack_id: int
    techstack_name: str
    description: str | None = None


class ProjectBase(BaseModel):
    project_name: str
    description: str
    links: LinkBase = LinkBase()


class ProjectCreate(ProjectBase):
    domain_ids: list[int] = []
    techstack_ids: list[int] = []


class ProjectUpdate(BaseModel):
    project_name: str | None = None
    description: str | None = None
    links: LinkBase | None = None
    domain_ids: list[int] | None = None
    techstack_ids: list[int] | None = None


class ProjectRead(ProjectBase):
    project_id: int
    domains: list[DomainRead] = []
    techstacks: list[TechStackRead] = []
    createdAt: datetime
    updatedAt: datetime | None = None
