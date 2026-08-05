from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.projects import Projects

from app.models.base import Base

class TechStacks(Base):
    __tablename__ = 'tech_stacks'

    techstack_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    techstack_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )
    
    description: Mapped[str] = mapped_column(
        String(255)
    )

    projects: Mapped[List["Projects"]] = relationship(
        secondary="project_techstacks",
        back_populates="techstacks"
    )
