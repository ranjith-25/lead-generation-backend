from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.project_domains import ProjectDomain
from app.exceptions.database import get_database_message
from sqlalchemy.exc import SQLAlchemyError

import logging
async def get_project_domains(db: AsyncSession):
    try:
        projectDomainsList = await db.execute(select(ProjectDomain))
        projectDomainsList = projectDomainsList.scalars().all()
        return projectDomainsList
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Project Domains")
        raise e

async def get_project_domain_by_id(db: AsyncSession, projectDomainID: int):
    try:
        projectDomainsDetails = await db.execute(select(ProjectDomain).where(ProjectDomain.id == projectDomainID))
        projectDomainsDetails = projectDomainsDetails.scalars().first()

        return projectDomainsDetails
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Project Domains")
        raise e

async def create_project_domain(db: AsyncSession, projectDomain: ProjectDomain):
    try:
        db.add(projectDomain)
        await db.commit()
        await db.refresh(projectDomain)
        return projectDomain
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Project Domain")
        raise e


async def update_project_domain(
    db: AsyncSession,
    project_domain: dict,
    domain_id : int
):
    try:
        result = await db.execute(
            select(ProjectDomain).where(
                ProjectDomain.id == domain_id
            )
        )

        db_project_domain = result.scalars().first()

        if not db_project_domain:
            return None

        for key, value in project_domain.items():
            if key != "id":
                setattr(db_project_domain, key, value)

        await db.commit()
        await db.refresh(db_project_domain)

        return db_project_domain

    except SQLAlchemyError:
        await db.rollback()
        logging.exception("Could not update Project Domain")
        raise

async def delete_project_domain(db: AsyncSession, projectDomainID: int):
    try:
        projectDomainsDetails = await db.execute(select(ProjectDomain).where(ProjectDomain.id == projectDomainID))
        projectDomainsDetails = projectDomainsDetails.scalars().first()
        await db.delete(projectDomainsDetails)
        await db.commit()
        return projectDomainsDetails
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Project Domain")
        raise e


    
