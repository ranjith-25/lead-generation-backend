"""add soft delete to user_projects: is_deleted

Revision ID: c8d5e2a17f43
Revises: a71c9e4d5b03
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8d5e2a17f43'
down_revision: Union[str, None] = 'a71c9e4d5b03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default 'false' backfills every existing allocation as live in the same statement,
    # which is what lets the column be NOT NULL without a separate UPDATE pass. The default is
    # kept on the column (not dropped afterwards) so raw INSERTs that predate the model change
    # still produce a live row.
    #
    # No partial unique index here, unlike the `users` soft delete: `user_projects` carries no
    # uniqueness at all — the same person may hold several allocations on one project — so
    # there is no constraint that a soft-deleted row could wrongly keep occupied.
    op.add_column(
        'user_projects',
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
        ),
    )


def downgrade() -> None:
    # Drops the flag only. Rows soft-deleted while this migration was applied come back as
    # ordinary live allocations, since without the column there is nowhere to record deletion.
    op.drop_column('user_projects', 'is_deleted')
