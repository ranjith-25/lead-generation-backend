from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.sample import Sample
from app.schemas.sample import SampleCreate, SampleRead

router = APIRouter(prefix="/samples", tags=["samples"])


@router.post("/", response_model=SampleRead, status_code=201)
async def create_sample(data: SampleCreate, db: AsyncSession = Depends(get_db)) -> SampleRead:
    sample = Sample(**data.model_dump())
    db.add(sample)
    await db.flush()
    await db.refresh(sample)
    return SampleRead.model_validate(sample)


@router.get("/", response_model=list[SampleRead])
async def list_samples(db: AsyncSession = Depends(get_db)) -> list[SampleRead]:
    result = await db.execute(select(Sample).order_by(Sample.created_at.desc()))
    samples = result.scalars().all()
    return [SampleRead.model_validate(s) for s in samples]
