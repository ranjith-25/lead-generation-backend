from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.feature import Feature

async def add_feature_db(db: AsyncSession, feature: Feature) -> Feature:
    try:
        db.add(feature)
        await db.commit()
        await db.refresh(feature)
        return feature
    except SQLAlchemyError:
        await db.rollback()
        raise

async def get_feature_by_id_db(db: AsyncSession, feature_id: int) -> Feature | None:
    result = await db.execute(select(Feature).where(Feature.feature_id == feature_id))
    return result.scalars().first()

async def get_feature_by_key_db(db: AsyncSession, feature_key: str) -> Feature | None:
    result = await db.execute(select(Feature).where(Feature.feature_key == feature_key))
    return result.scalars().first()

async def get_all_features_db(db: AsyncSession) -> list[Feature]:
    result = await db.execute(select(Feature))
    return list(result.scalars().all())

async def update_feature_db(db: AsyncSession, feature: Feature, update_data: dict) -> Feature:
    try:
        for key, value in update_data.items():
            setattr(feature, key, value)
        await db.commit()
        await db.refresh(feature)
        return feature
    except SQLAlchemyError:
        await db.rollback()
        raise

async def delete_feature_db(db: AsyncSession, feature: Feature) -> None:
    try:
        await db.delete(feature)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise
