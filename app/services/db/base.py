import uuid
from abc import ABC
from typing import Generic, TypeVar, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):

    model: Type[ModelType]
    id_column = None

    def __init__(self, db: AsyncSession):
        self.db = db

    def _id_column(self):
        return self.id_column if self.id_column is not None else self.model.id

    async def get(self, id: uuid.UUID) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(self._id_column() == id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def bulk_create(self, items: list[dict]) -> list[ModelType]:
        objects = [self.model(**item) for item in items]

        self.db.add_all(objects)
        await self.db.commit()

        for obj in objects:
            await self.db.refresh(obj)

        return objects

    async def update(self, id: uuid.UUID, **kwargs) -> ModelType | None:
        obj = await self.get(id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: uuid.UUID) -> bool:
        obj = await self.get(id)
        if obj is None:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True