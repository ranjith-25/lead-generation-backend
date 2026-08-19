"""make users.role_id not null and switch its FK to RESTRICT

Revision ID: c3a91f2b7d10
Revises: b7e1c4a95f30
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c3a91f2b7d10'
down_revision: Union[str, None] = 'b7e1c4a95f30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The role every currently-roleless user lands on. Same role `handle_delete_role` reassigns
# onto (`RolesMap.USER`), spelled out as a literal so this migration never has to import
# application code that may have moved on by the time it runs.
FALLBACK_ROLE_NAME = "User"

# Postgres named this one, not us: the initial migration declared the FK inline inside
# create_table('users', ...) with no name, so it got the default <table>_<column>_fkey.
FK_NAME = "users_role_id_fkey"


def upgrade() -> None:
    bind = op.get_bind()

    null_users = bind.execute(
        sa.text("SELECT count(*) FROM users WHERE role_id IS NULL")
    ).scalar_one()

    if null_users:
        fallback_role_id = bind.execute(
            sa.text(
                'SELECT role_id FROM roles WHERE "roleName" = :role_name'
                ' ORDER BY "createdAt" LIMIT 1'
            ),
            {"role_name": FALLBACK_ROLE_NAME},
        ).scalar()

        # Stopping beats guessing. NULL is exactly what the new constraint forbids, and
        # picking some other role at random would quietly hand those accounts permissions
        # nobody granted them. Seed the fallback role - or assign those users by hand - and
        # run the migration again.
        if fallback_role_id is None:
            raise RuntimeError(
                f"{null_users} user(s) still have role_id IS NULL and the fallback role "
                f"'{FALLBACK_ROLE_NAME}' does not exist in `roles`. Create that role, or "
                "assign those users a role manually, before running this migration."
            )

        bind.execute(
            sa.text("UPDATE users SET role_id = :role_id WHERE role_id IS NULL"),
            {"role_id": fallback_role_id},
        )

    # SET NULL cannot survive alongside NOT NULL - deleting a role would ask Postgres to write
    # a NULL the column rejects, and the delete would fail on a constraint the caller never
    # mentioned. RESTRICT states the real rule instead: a role keeping users cannot be dropped.
    op.drop_constraint(FK_NAME, 'users', type_='foreignkey')
    op.alter_column('users', 'role_id',
               existing_type=postgresql.UUID(as_uuid=True),
               nullable=False)
    op.create_foreign_key(FK_NAME, 'users', 'roles', ['role_id'], ['role_id'],
                          ondelete='RESTRICT')


def downgrade() -> None:
    # The backfill is deliberately not undone: which users were roleless beforehand is not
    # recorded anywhere, so re-nulling any of them would be a guess.
    op.drop_constraint(FK_NAME, 'users', type_='foreignkey')
    op.alter_column('users', 'role_id',
               existing_type=postgresql.UUID(as_uuid=True),
               nullable=True)
    op.create_foreign_key(FK_NAME, 'users', 'roles', ['role_id'], ['role_id'],
                          ondelete='SET NULL')
