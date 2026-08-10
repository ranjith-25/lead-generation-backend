import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.pipeline_execution_status import PipelineExecutionStatusModel


async def get_all_pipeline_execution_statuses(db: AsyncSession, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit if limit else 0
        query = select(PipelineExecutionStatusModel)
        if limit:
            query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        pipeline_execution_statuses = result.scalars().all()

        count_query = select(func.count(PipelineExecutionStatusModel.id))
        total = await db.scalar(count_query)

        return pipeline_execution_statuses, total or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Execution Statuses")
        raise e


async def get_pipeline_execution_status_by_id(db: AsyncSession, pipeline_execution_status_id: UUID):
    try:
        result = await db.execute(
            select(PipelineExecutionStatusModel).where(PipelineExecutionStatusModel.id == pipeline_execution_status_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Pipeline Execution Status")
        raise e


async def create_pipeline_execution_status(db: AsyncSession, pipeline_execution_status: PipelineExecutionStatusModel):
    try:
        db.add(pipeline_execution_status)
        await db.commit()
        await db.refresh(pipeline_execution_status)
        return pipeline_execution_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Pipeline Execution Status")
        raise e


async def update_pipeline_execution_status(db: AsyncSession, update_data: dict, pipeline_execution_status_id: UUID):
    try:
        result = await db.execute(
            select(PipelineExecutionStatusModel).where(PipelineExecutionStatusModel.id == pipeline_execution_status_id)
        )
        db_pipeline_execution_status = result.scalars().first()

        if not db_pipeline_execution_status:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_pipeline_execution_status, key, value)

        await db.commit()
        await db.refresh(db_pipeline_execution_status)
        return db_pipeline_execution_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Pipeline Execution Status")
        raise e


async def delete_pipeline_execution_status(db: AsyncSession, pipeline_execution_status_id: UUID):
    try:
        result = await db.execute(
            select(PipelineExecutionStatusModel).where(PipelineExecutionStatusModel.id == pipeline_execution_status_id)
        )
        db_pipeline_execution_status = result.scalars().first()
        if not db_pipeline_execution_status:
            return None
        await db.delete(db_pipeline_execution_status)
        await db.commit()
        return db_pipeline_execution_status
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Pipeline Execution Status")
        raise e
