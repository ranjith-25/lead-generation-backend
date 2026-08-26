import uuid

from fastapi import APIRouter, Depends

from app.schemas.specialization import (
    SpecializationCreate,
    SpecializationOut,
    SpecializationUpdate,
)
from app.services.db import SpecializationRepository
from app.services.deps import get_specialization_repo
from app.services.specialization import (
    create_specialization as create_specialization_service,
    delete_specialization as delete_specialization_service,
    get_specialization as get_specialization_service,
    list_specializations as list_specializations_service,
    update_specialization as update_specialization_service,
)


router = APIRouter(prefix="/specialization", tags=["specialization"])


@router.get("/{id}", response_model=SpecializationOut)
async def get_specialization(
    id: uuid.UUID, repo: SpecializationRepository = Depends(get_specialization_repo)
):
    return await get_specialization_service(repo, id)


@router.get("/", response_model=list[SpecializationOut])
async def list_specializations(
    repo: SpecializationRepository = Depends(get_specialization_repo),
):
    return await list_specializations_service(repo)


@router.post("/", response_model=list[SpecializationOut])
async def create_specialization(
    payload: list[SpecializationCreate],
    repo: SpecializationRepository = Depends(get_specialization_repo),
):
    return await create_specialization_service(repo, payload)

@router.patch("/{id}", response_model=SpecializationOut)
async def update_specialization(
    id: uuid.UUID,
    payload: SpecializationUpdate,
    repo: SpecializationRepository = Depends(get_specialization_repo),
):
    return await update_specialization_service(repo, id, payload)


@router.delete("/{id}")
async def delete_specialization(
    id: uuid.UUID, repo: SpecializationRepository = Depends(get_specialization_repo)
):
    await delete_specialization_service(repo, id)
    return {"ok": True}