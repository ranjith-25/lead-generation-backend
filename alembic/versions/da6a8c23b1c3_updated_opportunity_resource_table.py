"""Updated Opportunity Resource Table

Revision ID: da6a8c23b1c3
Revises: 9034d04f645b
Create Date: 2026-08-12 14:30:49.935430
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "da6a8c23b1c3"
down_revision: Union[str, None] = "9034d04f645b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


approval_status_enum = postgresql.ENUM(
    "SELECTED",
    "APPROVED",
    "REJECTED",
    "SUGGESTED",
    name="approvalstatus",
)


def upgrade() -> None:
    # Create PostgreSQL ENUM type first
    approval_status_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    # Add status
    op.add_column(
        "pipeline_opportunity_resource",
        sa.Column(
            "status",
            approval_status_enum,
            nullable=False,
        ),
    )

    # Add rejected fields
    op.add_column(
        "pipeline_opportunity_resource",
        sa.Column(
            "rejected_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "pipeline_opportunity_resource",
        sa.Column(
            "reject_reason",
            sa.String(length=1000),
            nullable=True,
        ),
    )

    op.add_column(
        "pipeline_opportunity_resource",
        sa.Column(
            "rejected_by",
            sa.UUID(),
            nullable=True,
        ),
    )

    # Foreign key
    op.create_foreign_key(
        "fk_pipeline_opportunity_resource_rejected_by",
        "pipeline_opportunity_resource",
        "users",
        ["rejected_by"],
        ["user_id"],
        ondelete="SET NULL",
    )

    # Remove old boolean fields
    op.drop_column(
        "pipeline_opportunity_resource",
        "is_selected",
    )

    op.drop_column(
        "pipeline_opportunity_resource",
        "is_approved",
    )

    # One approved resource per opportunity
    op.create_index(
        "uq_one_approved_resource_per_opportunity",
        "pipeline_opportunity_resource",
        ["opportunity_id"],
        unique=True,
        postgresql_where=sa.text("status = 'APPROVED'"),
    )


def downgrade() -> None:
    # Drop index
    op.drop_index(
        "uq_one_approved_resource_per_opportunity",
        table_name="pipeline_opportunity_resource",
    )

    # Restore old columns
    op.add_column(
        "pipeline_opportunity_resource",
        sa.Column(
            "is_approved",
            sa.Boolean(),
            nullable=True,
        ),
    )

    op.add_column(
        "pipeline_opportunity_resource",
        sa.Column(
            "is_selected",
            sa.Boolean(),
            nullable=True,
        ),
    )

    # Drop foreign key
    op.drop_constraint(
        "fk_pipeline_opportunity_resource_rejected_by",
        "pipeline_opportunity_resource",
        type_="foreignkey",
    )

    # Drop new columns
    op.drop_column(
        "pipeline_opportunity_resource",
        "rejected_by",
    )

    op.drop_column(
        "pipeline_opportunity_resource",
        "reject_reason",
    )

    op.drop_column(
        "pipeline_opportunity_resource",
        "rejected_at",
    )

    op.drop_column(
        "pipeline_opportunity_resource",
        "status",
    )

    # Drop PostgreSQL ENUM
    approval_status_enum.drop(
        op.get_bind(),
        checkfirst=True,
    )