import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.pipeline_opportunity_project import PipelineOpportunityProjectModel


async def get_all_pipeline_opportunity_projects(db: AsyncSession, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit if limit else 0
        query = select(PipelineOpportunityProjectModel)
        if limit:
            query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        pipeline_opportunity_projects = result.scalars().all()

        count_query = select(func.count(PipelineOpportunityProjectModel.id))
        total = await db.scalar(count_query)

        return pipeline_opportunity_projects, total or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Projects")
        raise e


async def get_pipeline_opportunity_project_by_id(db: AsyncSession, pipeline_opportunity_project_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityProjectModel).where(PipelineOpportunityProjectModel.id == pipeline_opportunity_project_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Project")
        raise e


async def get_pipeline_opportunity_project_by_opportunity_id(db: AsyncSession, pipeline_opportunity_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityProjectModel).where(PipelineOpportunityProjectModel.opportunity_id == pipeline_opportunity_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Opportunity Project")
        raise e


async def create_pipeline_opportunity_project(db: AsyncSession, pipeline_opportunity_project: PipelineOpportunityProjectModel):
    try:
        db.add(pipeline_opportunity_project)
        await db.commit()
        await db.refresh(pipeline_opportunity_project)
        return pipeline_opportunity_project
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Pipeline Opportunity Project")
        raise e


async def create_multiple_pipeline_opportunity_project(db: AsyncSession, pipeline_opportunity_projects: list[PipelineOpportunityProjectModel]):
    try:
        db.add_all(pipeline_opportunity_projects)
        await db.commit()
        return pipeline_opportunity_projects
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Pipeline Opportunity Project")
        raise e


async def update_pipeline_opportunity_project(db: AsyncSession, update_data: dict, pipeline_opportunity_project_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityProjectModel).where(PipelineOpportunityProjectModel.id == pipeline_opportunity_project_id)
        )
        db_pipeline_opportunity_project = result.scalars().first()

        if not db_pipeline_opportunity_project:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_pipeline_opportunity_project, key, value)

        await db.commit()
        await db.refresh(db_pipeline_opportunity_project)
        return db_pipeline_opportunity_project
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Pipeline Opportunity Project")
        raise e


async def delete_pipeline_opportunity_project(db: AsyncSession, pipeline_opportunity_project_id: UUID):
    try:
        result = await db.execute(
            select(PipelineOpportunityProjectModel).where(PipelineOpportunityProjectModel.id == pipeline_opportunity_project_id)
        )
        db_pipeline_opportunity_project = result.scalars().first()
        if not db_pipeline_opportunity_project:
            return None
        await db.delete(db_pipeline_opportunity_project)
        await db.commit()
        return db_pipeline_opportunity_project
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Pipeline Opportunity Project")
        raise e
