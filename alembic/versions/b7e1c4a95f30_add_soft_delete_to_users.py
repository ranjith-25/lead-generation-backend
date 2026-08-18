"""add soft delete to users: is_deleted, deleted_at, partial unique email

Revision ID: b7e1c4a95f30
Revises: d83431234950
Create Date: 2026-08-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e1c4a95f30'
down_revision: Union[str, None] = 'd83431234950'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
        ),
    )
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # A plain UNIQUE on email would burn a soft-deleted user's address forever - the same
    # person could never be re-invited. Replace it with a unique index that only covers live
    # rows. IF EXISTS because the constraint was created implicitly by
    # sa.UniqueConstraint('email') in the initial migration, so its name is Postgres-generated.
    op.execute('ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key')
    op.create_index(
        'uq_users_email_active',
        'users',
        ['email'],
        unique=True,
        postgresql_where=sa.text('is_deleted = false'),
    )


def downgrade() -> None:
    # Reinstating the blanket UNIQUE fails if two rows share an email, which this migration
    # made legal. Resolve those duplicates before downgrading.
    op.drop_index('uq_users_email_active', table_name='users')
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'is_deleted')
