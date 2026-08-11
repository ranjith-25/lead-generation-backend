import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.pipeline_opportunity_resource import PipelineOpportunityResourceModel


async def get_all_pipeline_opportunity_resources(db: AsyncSession, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit if limit else 0
        query = select(PipelineOpportunityResourceModel)
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


async def get_pipeline_opportunity_resource_by_id(db: AsyncSession, pipeline_opportunity_resource_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel).where(PipelineOpportunityResourceModel.id == pipeline_opportunity_resource_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Resource")
        raise e


async def get_pipeline_opportunity_resource_by_opportunity_id(db: AsyncSession, pipeline_opportunity_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel).where(PipelineOpportunityResourceModel.opportunity_id == pipeline_opportunity_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Resource by opportunity id")
        raise e


async def create_pipeline_opportunity_resource(db: AsyncSession, pipeline_opportunity_resource: PipelineOpportunityResourceModel):
    try:
        db.add(pipeline_opportunity_resource)
        await db.commit()
        await db.refresh(pipeline_opportunity_resource)
        return pipeline_opportunity_resource
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


async def update_pipeline_opportunity_resource(db: AsyncSession, update_data: dict, pipeline_opportunity_resource_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel).where(PipelineOpportunityResourceModel.id == pipeline_opportunity_resource_id)
        )
        db_pipeline_opportunity_resource = result.scalars().first()

        if not db_pipeline_opportunity_resource:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_pipeline_opportunity_resource, key, value)

        await db.commit()
        await db.refresh(db_pipeline_opportunity_resource)
        return db_pipeline_opportunity_resource
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Pipeline Opportunity Resource")
        raise e


async def delete_pipeline_opportunity_resource(db: AsyncSession, pipeline_opportunity_resource_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityResourceModel).where(PipelineOpportunityResourceModel.id == pipeline_opportunity_resource_id)
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
