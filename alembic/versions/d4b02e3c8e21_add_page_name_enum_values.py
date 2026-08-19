"""add page_name enum values

Revision ID: d4b02e3c8e21
Revises: c3a91f2b7d10
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4b02e3c8e21'
down_revision: Union[str, None] = 'c3a91f2b7d10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The page_name enum was created at e3f7a1c65b04 with the one label opportunity_edit_history
# needed. The comments table serves three pages, so the type needs the other two. Both are
# also valid on opportunity_edit_history.page_name from here on — the type is shared.
NEW_PAGE_NAMES = (
    'RESOURCE_MATCH',
    'TECHNICAL_PREPARATION',
)


def upgrade() -> None:
    # ADD VALUE cannot be used by the same transaction that adds it, which is why the labels
    # land in their own revision rather than alongside e5c13f4d9f32, whose backfill inserts
    # rows carrying 'TECHNICAL_PREPARATION'.
    for page_name in NEW_PAGE_NAMES:
        op.execute(
            f"ALTER TYPE page_name ADD VALUE IF NOT EXISTS '{page_name}'"
        )


def downgrade() -> None:
    # Deliberate no-op, not an oversight. PostgreSQL cannot drop a label from an enum type;
    # undoing this would mean recreating page_name without these labels and rewriting every
    # column that uses it (opportunity_edit_history.page_name, comments.page_name), which is
    # not worth it for additive labels. Downgrading past this revision leaves the two extra
    # labels in place, unused and harmless.
    pass
