"""add notification user id

Revision ID: c6c7cf4cf2e1
Revises: 55cb3e5df204
Create Date: 2026-07-28 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c6c7cf4cf2e1"
down_revision: Union[str, Sequence[str], None] = "55cb3e5df204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("user_id", sa.UUID(), nullable=True))
    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )
    op.execute("UPDATE notifications SET user_id = wallet_id WHERE user_id IS NULL")
    op.alter_column("notifications", "user_id", nullable=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_column("notifications", "user_id")
