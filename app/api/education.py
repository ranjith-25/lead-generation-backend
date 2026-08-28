import uuid

from fastapi import APIRouter, Depends

from app.schemas.education import EducationCreate, EducationOut, EducationUpdate
from app.services.db import EducationRepository
from app.services.deps import get_education_repo
from app.services.education import (
    create_education as create_education_service,
    delete_education as delete_education_service,
    get_education as get_education_service,
    list_education as list_education_service,
    update_education as update_education_service,
)


router = APIRouter(prefix="/education", tags=["education"])


@router.get("/{id}", response_model=EducationOut)
async def get_education(
    id: uuid.UUID, repo: EducationRepository = Depends(get_education_repo)
):
    return await get_education_service(repo, id)


@router.get("/", response_model=list[EducationOut])
async def list_education(repo: EducationRepository = Depends(get_education_repo)):
    return await list_education_service(repo)


@router.post("/", response_model=list[EducationOut])
async def create_education(
    payload: list[EducationCreate],
    repo: EducationRepository = Depends(get_education_repo),
):
    return await create_education_service(repo, payload)


@router.patch("/{id}", response_model=EducationOut)
async def update_education(
    id: uuid.UUID,
    payload: EducationUpdate,
    repo: EducationRepository = Depends(get_education_repo),
):
    return await update_education_service(repo, id, payload)


@router.delete("/{id}")
async def delete_education(
    id: uuid.UUID, repo: EducationRepository = Depends(get_education_repo)
):
    await delete_education_service(repo, id)
    return {"ok": True}