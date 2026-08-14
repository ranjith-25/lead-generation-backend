"""add notification_type enum labels

Revision ID: c47f1a9d3b62
Revises: 2e4c2588f219
Create Date: 2026-08-14 12:05:41.204118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c47f1a9d3b62'
down_revision: Union[str, None] = '2e4c2588f219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The notification_type enum was created at 9232aa10c0ce with only five labels;
# app/config.py has grown to fourteen. These are the nine the type is missing.
NEW_NOTIFICATION_TYPES = (
    'RESOURCE_ASSIGNED_TO_TL',
    'RESOURCE_REJECTED',
    'RESOURCE_APPROVED',
    'RESOURCE_ASSIGNED',
    'RESOURCE_PENDING_APPROVAL',
    'TEAM_MEMBER_ASSIGNED',
    'TEAM_MEMBER_ASSIGNED_BYPASSED',
    'BD_RESOURCE_APPROVED',
    'BD_RESOURCE_REJECTED',
)


def upgrade() -> None:
    # ADD VALUE cannot be used by the same transaction that adds it, which is why the
    # labels land in their own revision rather than alongside the code that inserts them.
    for notification_type in NEW_NOTIFICATION_TYPES:
        op.execute(
            f"ALTER TYPE notification_type ADD VALUE IF NOT EXISTS '{notification_type}'"
        )


def downgrade() -> None:
    # PostgreSQL cannot drop a label from an enum type — undoing this would mean
    # recreating notification_type without these labels and rewriting every column that
    # uses it, which is not worth it for additive labels.
    pass
