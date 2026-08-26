"""backfill the on_project user_status key

Revision ID: d5f7b2c94a18
Revises: c7d4a1f9e320
Create Date: 2026-08-25 00:00:00.000000

c7d4a1f9e320 keyed only the rows the code addressed at the time, and 'on_project' was not one
of them — UserStatusKey.ON_PROJECT existed but nothing read it. `sync_project_status` reads it
now, and an unkeyed row makes that lookup return None, which the sync treats as "do nothing":
the allocation succeeds and the user silently stays on bench.

Data only, no schema change. Matched on the display name exactly as the on_bench backfill was,
case-insensitive and whitespace-tolerant because these are administrator-entered rows.

After applying, confirm the key landed:

    SELECT unnest(ARRAY['on_bench','on_project']) AS missing
    EXCEPT SELECT status_key FROM user_status WHERE status_key IS NOT NULL;

Zero rows expected. If 'on_project' is listed, this environment either renamed the row or never
had one — set the key by hand, or insert the status. No INSERT is attempted here: user_status
has NOT NULL `createdBy`/`updatedBy` FKs, so seeding a row would mean picking an arbitrary user
as its author.

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd5f7b2c94a18'
down_revision: Union[str, None] = 'c7d4a1f9e320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE user_status SET status_key = 'on_project'
        WHERE btrim(lower("displayName")) IN ('on project', 'on-project', 'onproject')
          AND status_key IS NULL
    """)


def downgrade() -> None:
    # Clears the key without touching the row itself — the status stays, it just stops being
    # addressable by the code, which is the state this revision found it in.
    op.execute("UPDATE user_status SET status_key = NULL WHERE status_key = 'on_project'")
