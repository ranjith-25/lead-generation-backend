import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.education import EducationCreate, EducationOut, EducationUpdate
from app.services.db import EducationRepository
from app.services.deps import get_education_repo


router = APIRouter(prefix="/education", tags=["education"])


@router.get("/{id}", response_model=EducationOut)
async def get_education(
    id: uuid.UUID, repo: EducationRepository = Depends(get_education_repo)
):
    obj = await repo.get(id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Education not found")
    return obj


@router.get("/", response_model=list[EducationOut])
async def list_education(repo: EducationRepository = Depends(get_education_repo)):
    return await repo.list()


@router.post("/", response_model=list[EducationOut])
async def create_education(
    payload: list[EducationCreate],
    repo: EducationRepository = Depends(get_education_repo),
):
    items = [item.model_dump() for item in payload]
    return await repo.bulk_create(items)


@router.patch("/{id}", response_model=EducationOut)
async def update_education(
    id: uuid.UUID,
    payload: EducationUpdate,
    repo: EducationRepository = Depends(get_education_repo),
):
    obj = await repo.update(id, **payload.model_dump(exclude_unset=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Education not found")
    return obj


@router.delete("/{id}")
async def delete_education(
    id: uuid.UUID, repo: EducationRepository = Depends(get_education_repo)
):
    if not await repo.delete(id):
        raise HTTPException(status_code=404, detail="Education not found")
    return {"ok": True}