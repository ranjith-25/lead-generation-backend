from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sample import Sample


async def create_sample(db: AsyncSession, sample_data: dict) -> Sample:
    sample = Sample(**sample_data)
    db.add(sample)
    await db.flush()
    await db.refresh(sample)
    return sample


async def get_samples(db: AsyncSession) -> Sequence[Sample]:
    result = await db.execute(select(Sample).order_by(Sample.created_at.desc()))
    return result.scalars().all()
