import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.specialization import (
    SpecializationCreate,
    SpecializationOut,
    SpecializationUpdate,
)
from app.services.db import SpecializationRepository
from app.services.deps import get_specialization_repo


router = APIRouter(prefix="/specialization", tags=["specialization"])


@router.get("/{id}", response_model=SpecializationOut)
async def get_specialization(
    id: uuid.UUID, repo: SpecializationRepository = Depends(get_specialization_repo)
):
    obj = await repo.get(id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Specialization not found")
    return obj


@router.get("/", response_model=list[SpecializationOut])
async def list_specializations(
    repo: SpecializationRepository = Depends(get_specialization_repo),
):
    return await repo.list()


@router.post("/", response_model=SpecializationOut)
async def create_specialization(
    payload: SpecializationCreate,
    repo: SpecializationRepository = Depends(get_specialization_repo),
):
    return await repo.create(**payload.model_dump())


@router.patch("/{id}", response_model=SpecializationOut)
async def update_specialization(
    id: uuid.UUID,
    payload: SpecializationUpdate,
    repo: SpecializationRepository = Depends(get_specialization_repo),
):
    obj = await repo.update(id, **payload.model_dump(exclude_unset=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Specialization not found")
    return obj


@router.delete("/{id}")
async def delete_specialization(
    id: uuid.UUID, repo: SpecializationRepository = Depends(get_specialization_repo)
):
    if not await repo.delete(id):
        raise HTTPException(status_code=404, detail="Specialization not found")
    return {"ok": True}