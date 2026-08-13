from sqlalchemy import Select, or_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config import SortOrder
from app.models.projects import Projects
from app.schemas.project import ProjectFilters
from app.models.project_domains import ProjectDomain
from app.models.techstacks import TechStacks
from app.services.db.filters import apply_sort, apply_time_range

# Field names the API accepts for `sort_by`, mapped to the column each one sorts on.
# Domain and techstack are excluded: they are filtered via EXISTS, and sorting on them
# would need the join this query deliberately avoids.
PROJECT_SORTABLE = {
    "project_name": Projects.project_name,
    "createdAt": Projects.createdAt,
    "updatedAt": Projects.updatedAt,
    "is_draft": Projects.is_draft,
}


def _apply_project_filters(query: Select, filters: ProjectFilters) -> Select:
    """The list filters are applied as EXISTS (`has`/`any`) rather than joins.

    A project may sit in several of the requested techstacks; joining the junction
    would return it once per match, which would both duplicate it in the page and
    inflate the total. EXISTS matches the row at most once.
    """

    query = apply_time_range(query, Projects.createdAt, filters.time_filter)

    if filters.search and filters.search != "string":
        query = query.where(
            or_(
                Projects.project_name.ilike(f"%{filters.search}%"),
                Projects.description.ilike(f"%{filters.search}%")
            )
        )

    if filters.project_domains and "string" not in filters.project_domains:
        query = query.where(
            Projects.projectDomain.has(
                ProjectDomain.domain.in_(filters.project_domains)
            )
        )

    if filters.project_techstacks and "string" not in filters.project_techstacks:
        query = query.where(
            Projects.techstacks.any(
                TechStacks.techstack_name.in_(filters.project_techstacks)
            )
        )

    return query


async def get_all_projects_db(
    db: AsyncSession,
    filters: ProjectFilters,
) -> tuple[list[Projects], int]:

    total_column = func.count().over().label("total")

    query = apply_sort(
        _apply_project_filters(select(Projects, total_column), filters),
        PROJECT_SORTABLE,
        filters.sort_by,
        filters.order_by,
        # project_id kept as the fallback so paging stays stable for callers that
        # never send a sort — it is the only column guaranteed unique here.
        default_column=Projects.project_id,
        default_order=SortOrder.ASC,
    )

    if filters.limit is not None:
        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)

    rows = (await db.execute(query)).all()

    if rows:
        return [row[0] for row in rows], rows[0].total

    # an empty page carries no window value; only a page past the end can still have a
    # total, so the extra count is paid for that case alone
    total = await count_projects_db(db, filters) if filters.page > 1 else 0
    return [], total


async def count_projects_db(db: AsyncSession, filters: ProjectFilters) -> int:
    query = _apply_project_filters(select(func.count(Projects.project_id)), filters)
    return (await db.execute(query)).scalar_one()


async def get_project_by_id_db(db: AsyncSession, project_id: UUID) -> Projects | None:
    result = await db.execute(select(Projects).where(Projects.project_id == project_id))
    return result.scalars().first()

async def get_project_by_ids_list_db(db: AsyncSession, project_ids: list[UUID]) -> list[Projects] | None:
    result = await db.execute(select(Projects).where(Projects.project_id.in_(project_ids)))
    return list(result.scalars().all())


async def get_project_by_name_db(db: AsyncSession, project_name: str) -> Projects | None:
    result = await db.execute(select(Projects).where(Projects.project_name == project_name))
    return result.scalars().first()


async def add_project_db(db: AsyncSession, project: Projects) -> Projects:
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project_db(db: AsyncSession, project: Projects, update_data: dict) -> Projects:
    for key, value in update_data.items():
        setattr(project, key, value)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project_db(db: AsyncSession, project: Projects) -> None:
    await db.delete(project)
    await db.commit()
