import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.pipeline_opportunity_techincal_preperation import PipelineOpportunityTechnicalPreperationModel


async def get_all_pipeline_opportunity_technical_preperations(db: AsyncSession, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit if limit else 0
        query = select(PipelineOpportunityTechnicalPreperationModel)
        if limit:
            query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        pipeline_opportunity_technical_preperations = result.scalars().all()

        count_query = select(func.count(PipelineOpportunityTechnicalPreperationModel.id))
        total = await db.scalar(count_query)

        return pipeline_opportunity_technical_preperations, total or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Technical Preperations")
        raise e


async def get_pipeline_opportunity_technical_preperation_by_id(db: AsyncSession, pipeline_opportunity_technical_preperation_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityTechnicalPreperationModel).where(PipelineOpportunityTechnicalPreperationModel.id == pipeline_opportunity_technical_preperation_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Technical Preperation")
        raise e


async def get_pipeline_opportunity_technical_preperation_by_opportunity_id(db: AsyncSession, pipeline_opportunity_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityTechnicalPreperationModel).where(PipelineOpportunityTechnicalPreperationModel.opportunity_id == pipeline_opportunity_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Technical Preperation by opportunity id")
        raise e


async def create_pipeline_opportunity_technical_preperation(db: AsyncSession, pipeline_opportunity_technical_preperation: PipelineOpportunityTechnicalPreperationModel):
    try:
        db.add(pipeline_opportunity_technical_preperation)
        await db.commit()
        await db.refresh(pipeline_opportunity_technical_preperation)
        return pipeline_opportunity_technical_preperation
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Pipeline Opportunity Technical Preperation")
        raise e


async def create_multiple_pipeline_opportunity_technical_preperation(db: AsyncSession, pipeline_opportunity_technical_preperations: list[PipelineOpportunityTechnicalPreperationModel]):
    try:
        db.add_all(pipeline_opportunity_technical_preperations)
        await db.commit()
        return pipeline_opportunity_technical_preperations
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Pipeline Opportunity Technical Preperation")
        raise e


async def update_pipeline_opportunity_technical_preperation(db: AsyncSession, update_data: dict, pipeline_opportunity_technical_preperation_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityTechnicalPreperationModel).where(PipelineOpportunityTechnicalPreperationModel.id == pipeline_opportunity_technical_preperation_id)
        )
        db_pipeline_opportunity_technical_preperation = result.scalars().first()

        if not db_pipeline_opportunity_technical_preperation:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_pipeline_opportunity_technical_preperation, key, value)

        await db.commit()
        await db.refresh(db_pipeline_opportunity_technical_preperation)
        return db_pipeline_opportunity_technical_preperation
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Pipeline Opportunity Technical Preperation")
        raise e


async def delete_pipeline_opportunity_technical_preperation(db: AsyncSession, pipeline_opportunity_technical_preperation_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityTechnicalPreperationModel).where(PipelineOpportunityTechnicalPreperationModel.id == pipeline_opportunity_technical_preperation_id)
        )
        db_pipeline_opportunity_technical_preperation = result.scalars().first()
        if not db_pipeline_opportunity_technical_preperation:
            return None
        await db.delete(db_pipeline_opportunity_technical_preperation)
        await db.commit()
        return db_pipeline_opportunity_technical_preperation
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Pipeline Opportunity Technical Preperation")
        raise e
