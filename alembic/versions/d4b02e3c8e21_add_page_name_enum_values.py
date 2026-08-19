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
#
# The obvious ALTER TYPE ... ADD VALUE is what does NOT work here. PostgreSQL refuses to let a
# transaction *use* a label it added itself ("unsafe use of new value ... of enum type"), and
# alembic/env.py runs the whole upgrade in one transaction, so putting the labels in their own
# revision changes nothing — e5c13f4d9f32's backfill inserts 'TECHNICAL_PREPARATION' rows in
# that same transaction and fails.
#
# Recreating the type sidesteps the restriction: labels of a type CREATEd in the current
# transaction are usable immediately, because only ALTER TYPE ... ADD VALUE marks a label as
# uncommitted. The rename-recreate-recast-drop dance below therefore keeps the upgrade in a
# single transaction, which the alternative (transaction_per_migration in env.py) would give
# up for every migration in the repo.
#
# ALTER COLUMN ... TYPE rebuilds the dependent index (ix_opportunity_edit_history_page_name)
# on its own. opportunity_edit_history.page_name is the only column on the old type at this
# point — comments.page_name arrives one revision later — and it carries no default, so
# nothing needs to be dropped and restored around the cast.
#
# Each statement goes out on its own: asyncpg prepares every string it is handed, and a
# prepared statement may carry exactly one command.
RECREATE_PAGE_NAME = (
    "ALTER TYPE page_name RENAME TO page_name__old",
    """
    CREATE TYPE page_name AS ENUM (
        'OPPORTUNITY_ANALYSIS',
        'RESOURCE_MATCH',
        'TECHNICAL_PREPARATION'
    )
    """,
    """
    ALTER TABLE opportunity_edit_history
        ALTER COLUMN page_name TYPE page_name USING page_name::text::page_name
    """,
    "DROP TYPE page_name__old",
)


def upgrade() -> None:
    for statement in RECREATE_PAGE_NAME:
        op.execute(statement)


def downgrade() -> None:
    # Deliberate no-op, not an oversight. Reversing this would mean recreating page_name
    # without the two labels, which fails outright the moment any row already uses them
    # (opportunity_edit_history.page_name, comments.page_name) — and the whole point of the
    # revision is that those rows exist. Downgrading past it leaves the extra labels in
    # place, unused and harmless.
    pass
