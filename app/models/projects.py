from datetime import datetime
from typing import List

from sqlalchemy import DateTime, func, String,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Projects(Base):
    __tablename__= 'projects'

    project_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    project_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    description: Mapped[str] = mapped_column(
        String(255)
    )

    case_study: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    app_link: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # many projects can have many domains
    projectDomainID: Mapped[int] = mapped_column(
    ForeignKey("project_domains.id"),
    nullable=False
    )

    projectDomain: Mapped["ProjectDomain"] = relationship(
        back_populates="projects"
    )

    # many projects can have many techstacks
    techstacks: Mapped[List["TechStacks"]] = relationship(
        secondary="project_techstacks",
        back_populates="projects",
        lazy="selectin"
    )

    createdAt: Mapped[datetime] = mapped_column(
            DateTime,
            server_default=func.now()
        )

    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    @property
    def links(self) -> dict:
        return {"case_study": self.case_study, "app_link": self.app_link}
