"""add log_action enum values

Revision ID: f0a3c7d21b48
Revises: e5c13f4d9f32
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0a3c7d21b48'
down_revision: Union[str, None] = 'e5c13f4d9f32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The log_action enum was created at d83431234950 with the 42 actions that existed then.
# LogAction in app/config.py has grown to 49; these are the seven the type is missing, and
# every one of them has a live call site that fails with
# "invalid input value for enum log_action" until the label exists.
NEW_LOG_ACTIONS = (
    'COMMENT_ADDED',
    'COMMENT_REPLIED',
    'COMMENT_UPDATED',
    'COMMENT_DELETED',
    'USER_DELETED',
    'USER_BENCHED',
    'USER_HIERARCHY_REPAIRED',
)


def upgrade() -> None:
    # ADD VALUE cannot be used by the same transaction that adds it, which is why the labels
    # land in their own revision rather than alongside the code that inserts them.
    for log_action in NEW_LOG_ACTIONS:
        op.execute(
            f"ALTER TYPE log_action ADD VALUE IF NOT EXISTS '{log_action}'"
        )


def downgrade() -> None:
    # PostgreSQL cannot drop a label from an enum type — undoing this would mean recreating
    # log_action without these labels and rewriting system_logs.action, which is not worth it
    # for additive labels. Downgrading past this revision leaves them in place and unused.
    pass
