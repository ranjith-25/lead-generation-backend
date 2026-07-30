from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.postgres import get_db
from app.models.sample import Sample
from app.schemas.sample import SampleCreate, SampleRead
from app.services.db.sample import create_sample, get_samples

router = APIRouter(prefix="/samples", tags=["samples"])


@router.post("/", response_model=SampleRead, status_code=201)
async def create_sample_endpoint(data: SampleCreate, db: AsyncSession = Depends(get_db)) -> SampleRead:
    sample = await create_sample(db, data.model_dump())
    return SampleRead.model_validate(sample)


@router.get("/", response_model=list[SampleRead])
async def list_samples_endpoint(db: AsyncSession = Depends(get_db)) -> list[SampleRead]:
    samples = await get_samples(db)
    return [SampleRead.model_validate(s) for s in samples]
