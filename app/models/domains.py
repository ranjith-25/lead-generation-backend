from typing import List

from app.models.base import Base
from sqlalchemy import String

from sqlalchemy.orm import Mapped, mapped_column, relationship

class Domains( Base ):
    __tablename__ = "domains"

    domain_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    domain_name: Mapped[str] = mapped_column(
        unique=True
    )
    
    description: Mapped[str] = mapped_column(
        String(255)
    )

    projects: Mapped[List["Projects"]] = relationship(
        secondary="project_domains",
        back_populates="domains"
    )