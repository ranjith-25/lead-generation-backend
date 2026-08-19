from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.opportunity import Opportunity
from app.models.opportunity_status import OpportunityStatus
from app.schemas.opportunity import OpportunityFilterRequest
from app.schemas.common import get_time_filter_options
from app.models.platform import Platform
from app.models.user import User
from app.models.user_personal_info import UserPersonalInfo
from app.services.hierarchy import handleGetHierarchyByUser
from app.schemas.user import UserHierarchy
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.services.db.filters import apply_date_filters, apply_sort
from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel

# Field names the API accepts for `sort_by`, mapped to the column each one sorts on.
OPPORTUNITY_SORTABLE = {
    "title": Opportunity.title,
    "company": Opportunity.company,
    "role": Opportunity.role,
    "location": Opportunity.location,
    "platform": Opportunity.platform,
    "createdAt": Opportunity.createdAt,
    "updatedAt": Opportunity.updatedAt,
}

def extract_hierarchy_user_ids(node: UserHierarchy) -> list[UUID]:
    if not node:
        return []
    ids = [node.user_id]
    for child in node.children:
        ids.extend(extract_hierarchy_user_ids(child))
    return ids

def extract_hierarchy_users(node: UserHierarchy) -> list[dict]:
    if not node:
        return []
    users = [{"user_id": node.user_id, "fullName": node.fullName}]
    for child in node.children:
        users.extend(extract_hierarchy_users(child))
    return users

from sqlalchemy import select, or_, func, and_

async def addOpportunity(opportunity : Opportunity,db: AsyncSession) -> Opportunity:
    try:
        db.add(opportunity)
        await db.commit()
        await db.refresh(opportunity)
        return opportunity

    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Technical Preperations")
        raise e

from sqlalchemy import select, func, and_, or_, exists


async def get_all_opportunities(
    db: AsyncSession,
    user_id,
    filters: OpportunityFilterRequest | None = None,
    applyPagination : bool = True
) -> tuple[list[Opportunity], int]:

    target_user_ids = [user_id]

    if filters and filters.view == "Team view":
        hierarchy_res = await handleGetHierarchyByUser(db, user_id)

        if hierarchy_res.hierarchy:
            target_user_ids = extract_hierarchy_user_ids(
                hierarchy_res.hierarchy
            )

    # ---------------------------------------------------------
    # Resource visibility
    # ---------------------------------------------------------
    resource_access = exists(
        select(1)
        .select_from(PipelineOpportunityResourceModel)
        .where(
            and_(
                PipelineOpportunityResourceModel.opportunity_id
                == Opportunity.opportunityID,

                or_(
                    PipelineOpportunityResourceModel.user_id.in_(target_user_ids),
                    PipelineOpportunityResourceModel.approved_by.in_(target_user_ids),
                    PipelineOpportunityResourceModel.assigned_to_tl_by.in_(target_user_ids),
                    PipelineOpportunityResourceModel.rejected_by.in_(target_user_ids),
                ),
            )
        ).order_by(PipelineOpportunityResourceModel.updatedAt)
    )

    # ---------------------------------------------------------
    # Opportunity visibility
    # ---------------------------------------------------------
    query = select(Opportunity).where(
        or_(
            Opportunity.createdBy.in_(target_user_ids),
            resource_access,
        )
    )

    # ---------------------------------------------------------
    # Date filter - preset window or explicit from/to range
    # ---------------------------------------------------------
    if filters:
        query = apply_date_filters(
            query,
            Opportunity.createdAt,
            filters.time_filter,
            filters.from_date,
            filters.to_date,
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------
    if filters:
        if filters.search:
            search_term = f"%{filters.search.strip()}%"

            query = query.outerjoin(Opportunity.assigned_user)
            query = query.outerjoin(
                UserPersonalInfo,
                User.user_id == UserPersonalInfo.user_id,
            )

            query = query.where(
                or_(
                    Opportunity.title.ilike(search_term),
                    Opportunity.company.ilike(search_term),
                    Opportunity.location.ilike(search_term),
                    Opportunity.platform.ilike(search_term),
                    UserPersonalInfo.first_name.ilike(search_term),
                    UserPersonalInfo.last_name.ilike(search_term),
                )
            )

        if filters.platform:
            query = query.where(
                Opportunity.platform.in_(filters.platform)
            )

        if filters.company:
            query = query.where(
                Opportunity.company.in_(filters.company)
            )

        if filters.role:
            query = query.where(
                Opportunity.role.in_(filters.role)
            )

        if filters.location:
            query = query.where(
                Opportunity.location.in_(filters.location)
            )

        if filters.status:
            query = query.join(Opportunity.status).where(
                OpportunityStatus.status.in_(filters.status)
            )

        if filters.team:
            query = query.where(
                Opportunity.assigned_to.in_(filters.team)
            )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------
    count_query = select(func.count()).select_from(
        query.subquery()
    )

    total_result = await db.execute(count_query)
    total_count = total_result.scalar() or 0

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------
    query = apply_sort(
        query,
        OPPORTUNITY_SORTABLE,
        filters.sort_by if filters else None,
        filters.order_by if filters else None,
        default_column=Opportunity.updatedAt,
    )

    # ---------------------------------------------------------
    # Pagination
    # -------------------------------------------------------

    # Apply pagination
    if applyPagination and filters:
        query = query.offset(
            (filters.page - 1) * filters.size
        ).limit(filters.size)

    result = await db.execute(query)

    return list(result.scalars().all()), total_count

async def get_opportunity_filter_values(db: AsyncSession, user_id) -> dict:
    
    base_query = select(Opportunity).where(Opportunity.createdBy == user_id)
    
    # Fetch all available platforms and statuses from their respective tables
    platforms = await db.execute(select(Platform.name))
    companies = await db.execute(select(Opportunity.company).where(Opportunity.createdBy == user_id, Opportunity.company.is_not(None)).distinct())
    roles = await db.execute(select(Opportunity.role).where(Opportunity.createdBy == user_id, Opportunity.role.is_not(None)).distinct())
    locations = await db.execute(select(Opportunity.location).where(Opportunity.createdBy == user_id, Opportunity.location.is_not(None)).distinct())
    
    # Fetch all available statuses from the database table
    statuses = await db.execute(select(OpportunityStatus.status))
    
    # Fetch team
    hierarchy_res = await handleGetHierarchyByUser(db, user_id)
    team = extract_hierarchy_users(hierarchy_res.hierarchy) if hierarchy_res.hierarchy else []
    
    return {
        "platform": [p[0] for p in platforms.all()],
        "company": [c[0] for c in companies.all()],
        "role": [r[0] for r in roles.all()],
        "location": [l[0] for l in locations.all()],
        "status": [s[0] for s in statuses.all()],
        "team": team,
        "time_filter": get_time_filter_options(),
    }


async def get_opportunity_by_id(db: AsyncSession, opportunity_id, user_id) -> Opportunity | None:
    result = await db.execute(select(Opportunity).where(Opportunity.opportunityID == opportunity_id))
    return result.scalars().first()

async def get_opportunity_by_url(db: AsyncSession, job_posting_url: str) -> Opportunity | None:
    result = await db.execute(select(Opportunity).where(Opportunity.job_posting_url == job_posting_url))
    return result.scalars().first()

async def get_opportunity_details_by_id(db: AsyncSession, opportunity_id) -> Opportunity | None:
    result = await db.execute(select(Opportunity).where(Opportunity.opportunityID == opportunity_id))
    return result.scalars().first()

async def get_all_opportunity_statuses_db(db: AsyncSession) -> list[OpportunityStatus]:
    result = await db.execute(select(OpportunityStatus).order_by(OpportunityStatus.id))
    return list(result.scalars().all())

async def get_status_by_name(db: AsyncSession, status_name: str) -> OpportunityStatus | None:
    result = await db.execute(select(OpportunityStatus).where(OpportunityStatus.status == status_name))
    return result.scalars().first()

async def update_opportunity_db(db: AsyncSession, opportunity: Opportunity, update_data: dict) -> Opportunity:
    for key, value in update_data.items():
        setattr(opportunity, key, value)
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return opportunity

async def delete_opportunity_db(db: AsyncSession, opportunity: Opportunity) -> None:
    await db.delete(opportunity)
    await db.commit()

async def get_roles_count(db: AsyncSession, limit: int):
    query = (
    select(
        Opportunity.role,
        func.count(Opportunity.opportunityID).label("role_count"),
    )
    .where(Opportunity.role.is_not(None))
    .group_by(Opportunity.role)
    .order_by(func.count(Opportunity.opportunityID).desc())
    ).limit(limit)

    result = await db.execute(query)
    roles = result.all()
    
    return roles