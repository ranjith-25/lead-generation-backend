from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Feature(Base):
    __tablename__ = "features"

    feature_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    feature_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description : Mapped[str] =  mapped_column(
        String(255),
        nullable=True
    )

    parent_feature_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("features.feature_id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    parent: Mapped["Feature"] = relationship(
        remote_side=[feature_id],
        back_populates="children"
    )

    children: Mapped[list["Feature"]] = relationship(
        back_populates="parent"
    )