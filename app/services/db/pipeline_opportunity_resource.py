import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel
from app.models.user import User
from app.models.user_personal_info import UserPersonalInfo
from app.schemas.pipeline_opportunity_resource import ApprovalStatus,PipelineOpportunityResourceUpdate


def _get_resource_query_options():
    return [
        selectinload(PipelineOpportunityResourceModel.user_details)
        .selectinload(User.personal_info)
        .selectinload(UserPersonalInfo.jobRole),
        selectinload(PipelineOpportunityResourceModel.user_details)
        .selectinload(User.personal_info)
        .selectinload(UserPersonalInfo.userStatus),
        selectinload(PipelineOpportunityResourceModel.user_details)
        .selectinload(User.reportingUser)
        .selectinload(User.personal_info),
        selectinload(PipelineOpportunityResourceModel.approved_by_user)
        .selectinload(User.personal_info),
    ]


async def get_all_pipeline_opportunity_resources(db: AsyncSession, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit if limit else 0
        query = select(PipelineOpportunityResourceModel).options(*_get_resource_query_options())
        if limit:
            query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        pipeline_opportunity_resources = result.scalars().all()

        count_query = select(func.count(PipelineOpportunityResourceModel.id))
        total = await db.scalar(count_query)

        return pipeline_opportunity_resources, total or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Resources")
        raise e


async def get_pipeline_opportunity_resource_by_id(db: AsyncSession, pipeline_opportunity_resource_id: UUID | str):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel)
            .options(*_get_resource_query_options())
            .where(PipelineOpportunityResourceModel.id == pipeline_opportunity_resource_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e

async def get_multiple_pipeline_opportunity_resource_by_id(db: AsyncSession, pipeline_opportunity_resource_ids: list[UUID]):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel)
            .options(*_get_resource_query_options())
            .where(PipelineOpportunityResourceModel.id.in_(pipeline_opportunity_resource_ids))
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e


async def get_pipeline_opportunity_resource_by_opportunity_id(db: AsyncSession, pipeline_opportunity_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel)
            .options(*_get_resource_query_options())
            .where(PipelineOpportunityResourceModel.opportunity_id == pipeline_opportunity_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Resource by opportunity id")
        raise e


async def get_approved_pipeline_opportunity_resource_by_opportunity_id(
    db: AsyncSession, pipeline_opportunity_id: UUID
):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel)
            .where(PipelineOpportunityResourceModel.opportunity_id == pipeline_opportunity_id)
            .where(PipelineOpportunityResourceModel.status == ApprovalStatus.APPROVED)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find approved Pipeline Opportunity Resource by opportunity id")
        raise e


async def create_pipeline_opportunity_resource(db: AsyncSession, pipeline_opportunity_resource: PipelineOpportunityResourceModel):
    try:
        db.add(pipeline_opportunity_resource)
        await db.commit()
        await db.refresh(pipeline_opportunity_resource)
        return await get_pipeline_opportunity_resource_by_id(db, pipeline_opportunity_resource.id)
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Pipeline Opportunity Resource")
        raise e


async def create_multiple_pipeline_opportunity_resource(db: AsyncSession, pipeline_opportunity_resources: list[PipelineOpportunityResourceModel]):
    try:
        db.add_all(pipeline_opportunity_resources)
        await db.commit()
        return pipeline_opportunity_resources
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Pipeline Opportunity Resource")
        raise e


async def  update_pipeline_opportunity_resource(db: AsyncSession, update_data: dict, pipeline_opportunity_resource_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel)
            .options(*_get_resource_query_options())
            .where(PipelineOpportunityResourceModel.id == pipeline_opportunity_resource_id)
        )
        db_pipeline_opportunity_resource = result.scalars().first()

        if not db_pipeline_opportunity_resource:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_pipeline_opportunity_resource, key, value)

        await db.commit()
        return await get_pipeline_opportunity_resource_by_id(db, pipeline_opportunity_resource_id)
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Pipeline Opportunity Resource")
        raise e


async def delete_pipeline_opportunity_resource(db: AsyncSession, pipeline_opportunity_resource_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel)
            .options(*_get_resource_query_options())
            .where(PipelineOpportunityResourceModel.id == pipeline_opportunity_resource_id)
        )
        db_pipeline_opportunity_resource = result.scalars().first()
        if not db_pipeline_opportunity_resource:
            return None
        await db.delete(db_pipeline_opportunity_resource)
        await db.commit()
        return db_pipeline_opportunity_resource
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Pipeline Opportunity Resource")
        raise e


async def update_multiple_pipeline_opportunity_resource(
    db: AsyncSession,
    update_data: PipelineOpportunityResourceUpdate,
    pipeline_opportunity_resource_ids: list[UUID],
):
    try:
        result = await db.execute( 
            select(PipelineOpportunityResourceModel)
            .options(*_get_resource_query_options())
            .where(
                PipelineOpportunityResourceModel.id.in_(
                    pipeline_opportunity_resource_ids
                )
            )
        )

        db_pipeline_opportunity_resources = result.scalars().all()

        if not db_pipeline_opportunity_resources:
            return None

        # The ID is used to identify resources and must not be
        # modified as part of an update operation.
        update_data.pop("id", None)

        # Apply the same update fields to every selected resource.
        for resource in db_pipeline_opportunity_resources:
            for key, value in update_data.items():
                setattr(resource, key, value)

        await db.commit()

        # Refresh the objects so that updated values and relationships
        # are available after the transaction is committed.
        for resource in db_pipeline_opportunity_resources:
            await db.refresh(resource)

        return db_pipeline_opportunity_resources

    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception(
            "Could not update multiple Pipeline Opportunity Resources"
        )
        raise e