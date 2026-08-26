from uuid import UUID

import logging

logger = logging.getLogger(__name__)

from app.exceptions.custom import NotFoundException
from app.schemas.specialization import SpecializationCreate, SpecializationUpdate
from app.services.db.specialization import SpecializationRepository


async def get_specialization(repo: SpecializationRepository, specialization_id: UUID):
    specialization = await repo.get(specialization_id)
    if specialization is None:
        raise NotFoundException()
    return specialization


async def list_specializations(repo: SpecializationRepository):
    return await repo.list()

async def create_specialization(repo: SpecializationRepository,payload: list[SpecializationCreate]):
    items = [item.model_dump() for item in payload]

    created = await repo.bulk_create(items)

    logger.info(
        "Specialization bulk create: requested=%d created=%d skipped=%d",
        len(items),
        len(created),
        len(items) - len(created),
    )

    return created


# async def create_specialization(
#     repo: SpecializationRepository, payload: SpecializationCreate
# ):
#     return await repo.create(**payload.model_dump())


async def update_specialization(
    repo: SpecializationRepository,
    specialization_id: UUID,
    payload: SpecializationUpdate,
):
    specialization = await repo.update(
        specialization_id,
        **payload.model_dump(exclude_unset=True, exclude_none=True),
    )
    if specialization is None:
        raise NotFoundException()
    return specialization


async def delete_specialization(
    repo: SpecializationRepository, specialization_id: UUID
):
    if not await repo.delete(specialization_id):
        raise NotFoundException()