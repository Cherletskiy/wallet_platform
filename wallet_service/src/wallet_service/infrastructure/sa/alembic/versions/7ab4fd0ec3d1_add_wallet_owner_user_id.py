"""add wallet owner user id

Revision ID: 7ab4fd0ec3d1
Revises: 4d3f6d9a7c12
Create Date: 2026-07-27 19:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7ab4fd0ec3d1"
down_revision: Union[str, Sequence[str], None] = "4d3f6d9a7c12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("wallets", sa.Column("owner_user_id", sa.UUID(), nullable=True))
    op.create_index(
        op.f("ix_wallets_owner_user_id"),
        "wallets",
        ["owner_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_wallets_owner_user_id"), table_name="wallets")
    op.drop_column("wallets", "owner_user_id")
