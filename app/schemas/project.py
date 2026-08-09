import json
import re
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Form, Request
from fastapi.exceptions import RequestValidationError
from pydantic import AfterValidator, BaseModel, ConfigDict, TypeAdapter, ValidationError, Field
from pydantic_core import core_schema

MAX_LINK_KEY_LENGTH = 50
MAX_LINK_VALUE_LENGTH = 255

_LINK_KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]*$")
_BRACKET_KEY_PATTERN = re.compile(r"^links\[(?P<key>[^\]]+)\]$")

LINKS_EXAMPLE = '{"application": "www.something.com", "website": "www.something.com"}'
LINKS_DESCRIPTION = (
    "Links as an object of label -> URL. Send it either as a JSON object in this field, "
    'e.g. {"application": "www.something.com", "website": "www.something.com"}, or as one '
    "field per entry: links[application]=www.something.com. On update the whole map is replaced."
)


def _validate_links(value: dict[str, str]) -> dict[str, str]:
    """`links` is a free-form label -> URL map, so the keys are validated, not enumerated."""

    for key, url in value.items():
        if not _LINK_KEY_PATTERN.match(key) or len(key) > MAX_LINK_KEY_LENGTH:
            raise ValueError(
                f"link name '{key}' must be alphanumeric (spaces, '.', '_', '-' allowed) "
                f"and at most {MAX_LINK_KEY_LENGTH} characters"
            )
        if not url.strip():
            raise ValueError(f"link '{key}' has no URL")
        if len(url) > MAX_LINK_VALUE_LENGTH:
            raise ValueError(f"link '{key}' is longer than {MAX_LINK_VALUE_LENGTH} characters")

    return value


Links = Annotated[dict[str, str], AfterValidator(_validate_links)]

_LINKS_ADAPTER = TypeAdapter(Links)


class ProjectDomainRead(BaseModel):
    id: UUID
    domain: str
    description: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TechStackRead(BaseModel):
    techstack_id: UUID
    techstack_name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


def _validation_error(field: str, message: str, value):
    return RequestValidationError(
        [
            {
                "type": "value_error",
                "loc": ("body", field),
                "msg": message,
                "input": value,
            }
        ]
    )


def _validate_links_payload(payload) -> dict[str, str]:
    try:
        return _LINKS_ADAPTER.validate_python(payload)
    except ValidationError as exc:
        raise RequestValidationError(
            [
                {**error, "loc": ("body", "links", *error["loc"])}
                for error in exc.errors(include_url=False, include_context=False)
            ]
        )


def _parse_links(raw: str | None) -> dict[str, str] | None:
    """The whole map in one field, as a JSON object string."""

    if raw is None or not raw.strip():
        return None

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise _validation_error("links", "links must be a JSON object", raw)

    return _validate_links_payload(payload)


def _links_from_form(form) -> dict[str, str] | None:
    """One field per entry — `links[application]=...` — the way form encoders serialise a map."""

    collected = {
        match.group("key"): value
        for field, value in form.multi_items()
        if isinstance(value, str) and (match := _BRACKET_KEY_PATTERN.match(field))
    }
    return collected or None


def _resolve_links(raw: str | None, form) -> dict[str, str] | None:
    parsed = _parse_links(raw)
    if parsed is not None:
        return parsed

    bracketed = _links_from_form(form)
    return _validate_links_payload(bracketed) if bracketed is not None else None


TECHSTACK_IDS_DESCRIPTION = (
    "Ids of the tech stacks. Either one field per id (techstack_ids=1&techstack_ids=2) or a "
    "single comma-separated field (1,2) — Swagger's form UI sends the latter. On update the "
    "whole set is replaced; send clear_techstacks=true to remove them all."
)


def _split_comma_separated(value):
    """Swagger's multipart UI posts an array field as one comma-joined value, not repeated fields."""

    if not isinstance(value, list):
        return value

    expanded = []
    for item in value:
        if isinstance(item, str) and "," in item:
            expanded.extend(part.strip() for part in item.split(",") if part.strip())
        else:
            expanded.append(item)
    return expanded


class TechStackIds(list):
    """list[int] that also accepts one comma-separated field.

    The splitting lives on the type rather than in `Annotated[..., BeforeValidator(...)]`
    because FastAPI drops non-FastAPI metadata from a Form parameter's annotation, so a
    BeforeValidator there is silently ignored. Subclassing `list` also keeps FastAPI's
    sequence detection happy, so repeated fields are still read with `getlist`.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        return core_schema.no_info_before_validator_function(
            _split_comma_separated,
            handler.generate_schema(list[UUID]),
        )


def _build(model: type[BaseModel], payload: dict):
    try:
        return model(**payload)
    except ValidationError as exc:
        raise RequestValidationError(
            [
                {**error, "loc": ("body", *error["loc"])}
                for error in exc.errors(include_url=False, include_context=False)
            ]
        )


class ProjectBase(BaseModel):
    project_name: str
    description: str
    links: Links = {}
    is_draft: bool = True


class ProjectCreate(ProjectBase):
    projectDomainID: UUID
    techstack_ids: list[UUID] = []

    @classmethod
    async def as_form(
        cls,
        request: Request,
        project_name: str = Form(...),
        description: str = Form(...),
        projectDomainID: UUID = Form(...),
        is_draft: bool = Form(True),
        links: str | None = Form(None, description=LINKS_DESCRIPTION, examples=[LINKS_EXAMPLE]),
        techstack_ids: TechStackIds | None = Form(None, description=TECHSTACK_IDS_DESCRIPTION),
    ) -> "ProjectCreate":
        return _build(
            cls,
            {
                "project_name": project_name,
                "description": description,
                "projectDomainID": projectDomainID,
                "links": _resolve_links(links, await request.form()) or {},
                "techstack_ids": techstack_ids or [],
                "is_draft": is_draft
            },
        )


class ProjectUpdate(BaseModel):
    project_name: str | None = None
    description: str | None = None
    links: Links | None = None
    projectDomainID: UUID | None = None
    techstack_ids: list[UUID] | None = None
    is_draft: bool | None = None

    @classmethod
    async def as_form(
        cls,
        request: Request,
        project_name: str | None = Form(None),
        description: str | None = Form(None),
        projectDomainID: UUID | None = Form(None),
        is_draft: bool | None = Form(None),
        links: str | None = Form(None, description=LINKS_DESCRIPTION, examples=[LINKS_EXAMPLE]),
        techstack_ids: TechStackIds | None = Form(None, description=TECHSTACK_IDS_DESCRIPTION),
        clear_techstacks: bool = Form(False, description="Remove every techstack from the project"),
    ) -> "ProjectUpdate":
        # only the fields actually sent go into the model, so the service's `exclude_unset`
        # still distinguishes "omitted" from "set to null"
        payload = {}

        if project_name is not None:
            payload["project_name"] = project_name
        if description is not None:
            payload["description"] = description
        if projectDomainID is not None:
            payload["projectDomainID"] = projectDomainID
        if is_draft is not None:
            payload["is_draft"] = is_draft

        parsed_links = _resolve_links(links, await request.form())
        if parsed_links is not None:
            payload["links"] = parsed_links

        if techstack_ids is not None:
            payload["techstack_ids"] = techstack_ids
        elif clear_techstacks:
            # an empty form value cannot express this any more — the field is typed as integers
            payload["techstack_ids"] = []

        return _build(cls, payload)


class ProjectRead(ProjectBase):
    project_id: UUID
    projectDomain: ProjectDomainRead | None = None
    techstacks: list[TechStackRead] = []
    case_study: str | None = None
    createdAt: datetime
    updatedAt: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class ProjectFilters(BaseModel):
    search : str | None = None
    project_domains : list[str] | None = None
    project_techstacks : list[str] | None = None
    page: int = 1
    limit: int = 10

class AIProjectRequest(BaseModel):
    project_name : str = Field(...,description="Project Name")
    domain : str = Field(...,description="Project Domain")
    tech_stack : list[str] = Field(...,description="Tech Stack")
    description : str = Field(...,description="Project Description")