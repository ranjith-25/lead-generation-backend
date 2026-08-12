import json
from datetime import datetime
from typing import List, Optional
import uuid
from fastapi import Form, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ProfileVariantProjectBase(BaseModel):
    project_id: uuid.UUID
    project_name: str = Field(..., min_length=1, max_length=255)
    projectDomainID: uuid.UUID
    techstacks: List[str] = Field(..., description="List of tech stacks")
    description: str
    links: dict[str, str] = Field(default_factory=dict)


class ProfileVariantProjectDTO(ProfileVariantProjectBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileVariantProjectCreate(ProfileVariantProjectBase):
    pass


class ProfileVariantProjectUpdate(BaseModel):
    project_id: uuid.UUID
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    projectDomainID: Optional[uuid.UUID] = None
    techstacks: Optional[List[str]] = None
    description: Optional[str] = None
    links: Optional[dict[str, str]] = None


class ProfileVariantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: uuid.UUID = Field(..., description="Job Role ID")
    experience: str = Field(..., min_length=1, max_length=255)
    highlighted_skills: List[str] = Field(..., description="List of highlighted skills")
    upload_profile: str = Field(..., max_length=255)
    certificate: Optional[List[str]] = Field(None, description="List of certificates")
    is_draft: bool = Field(True)
    user_id: uuid.UUID = Field(..., description="Associated User ID")


class ProfileVariantDTO(ProfileVariantBase):
    profile_variant_id: uuid.UUID
    created_by: uuid.UUID
    updated_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    projects: List[ProfileVariantProjectDTO] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


def _parse_list_field(value: list[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        expanded = []
        for item in value:
            if isinstance(item, str) and item.startswith("[") and item.endswith("]"):
                try:
                    parsed = json.loads(item)
                    if isinstance(parsed, list):
                        expanded.extend(str(x) for x in parsed)
                        continue
                except Exception:
                    pass
            if isinstance(item, str) and "," in item:
                expanded.extend(part.strip() for part in item.split(",") if part.strip())
            else:
                expanded.append(item)
        return expanded

    stripped = value.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass
    if "," in stripped:
        return [part.strip() for part in stripped.split(",") if part.strip()]
    return [stripped] if stripped else []


def _parse_projects(raw: str | list | None) -> list[dict]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        payload = json.loads(raw)
        if isinstance(payload, list):
            return payload
        raise ValueError("projects must be a JSON array")
    except json.JSONDecodeError:
        raise ValueError("projects must be a valid JSON string")


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


class ProfileVariantCreate(ProfileVariantBase):
    projects: List[ProfileVariantProjectCreate] = Field(default_factory=list)

    @classmethod
    async def as_form(
        cls,
        request: Request,
        name: str = Form(...),
        role: uuid.UUID = Form(...),
        experience: str = Form(...),
        highlighted_skills: list[str] = Form(...),
        certificate: list[str] | None = Form(None),
        is_draft: bool = Form(True),
        user_id: uuid.UUID = Form(...),
        projects: str | None = Form(None),
    ) -> "ProfileVariantCreate":
        parsed_skills = _parse_list_field(highlighted_skills)
        parsed_cert = _parse_list_field(certificate) if certificate is not None else None
        parsed_projects = _parse_projects(projects)

        return _build(
            cls,
            {
                "name": name,
                "role": role,
                "experience": experience,
                "highlighted_skills": parsed_skills,
                "certificate": parsed_cert,
                "is_draft": is_draft,
                "user_id": user_id,
                "projects": parsed_projects,
                "upload_profile": "temp"
            }
        )


class ProfileVariantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[uuid.UUID] = Field(None, description="Job Role ID")
    experience: Optional[str] = Field(None, min_length=1, max_length=255)
    highlighted_skills: Optional[List[str]] = Field(None, description="List of highlighted skills")
    upload_profile: Optional[str] = Field(None, max_length=255)
    certificate: Optional[List[str]] = Field(None, description="List of certificates")
    is_draft: Optional[bool] = Field(None)
    user_id: Optional[uuid.UUID] = Field(None, description="Associated User ID")
    projects: Optional[List[ProfileVariantProjectUpdate]] = Field(None)


class DownloadProfileRequest(BaseModel):
    user_id: uuid.UUID
    profile_variant_id: uuid.UUID