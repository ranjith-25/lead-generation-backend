from uuid import UUID

from app.exceptions.custom import NotFoundException
from app.schemas.education import EducationCreate, EducationUpdate
from app.services.db.education import EducationRepository
import logging

logger = logging.getLogger(__name__)


async def get_education(repo: EducationRepository, education_id: UUID):
    education = await repo.get(education_id)
    if education is None:
        raise NotFoundException()
    return education


async def list_education(repo: EducationRepository):
    return await repo.list()


async def create_education(repo: EducationRepository,payload: list[EducationCreate]):
    items = [item.model_dump() for item in payload]

    created = await repo.bulk_create(items)

    logger.info(
        "Education bulk create: requested=%d created=%d skipped=%d",
        len(items),
        len(created),
        len(items) - len(created),
    )

    return created


async def update_education(
    repo: EducationRepository, education_id: UUID, payload: EducationUpdate
):
    education = await repo.update(
        education_id, **payload.model_dump(exclude_unset=True, exclude_none=True)
    )
    if education is None:
        raise NotFoundException()
    return education


async def delete_education(repo: EducationRepository, education_id: UUID):
    if not await repo.delete(education_id):
        raise NotFoundException()