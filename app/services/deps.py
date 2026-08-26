# app/api/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db import EducationRepository
from app.services.db import SpecializationRepository
from app.core.connections.postgres import get_db

def get_education_repo(db: AsyncSession = Depends(get_db)) -> EducationRepository:
    return EducationRepository(db)

def get_specialization_repo(db: AsyncSession = Depends(get_db)) -> SpecializationRepository:
    return SpecializationRepository(db)