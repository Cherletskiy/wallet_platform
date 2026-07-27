"""initial migration

Revision ID: 55cb3e5df204
Revises:
Create Date: 2026-07-27 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "55cb3e5df204"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    wallet_operation_type = sa.Enum(
        "DEPOSIT",
        "WITHDRAWAL",
        name="walletoperationtype",
    )
    wallet_operation_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_event_id", sa.UUID(), nullable=False),
        sa.Column("wallet_id", sa.UUID(), nullable=False),
        sa.Column("operation_type", wallet_operation_type, nullable=False),
        sa.Column("amount_cent", sa.Integer(), nullable=False),
        sa.Column("balance_cent", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_event_id",
            name="uq_notifications_source_event_id",
        ),
    )
    op.create_index(
        op.f("ix_notifications_created_at"),
        "notifications",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_source_event_id"),
        "notifications",
        ["source_event_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_notifications_wallet_id"),
        "notifications",
        ["wallet_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_wallet_id"), table_name="notifications")
    op.drop_index(
        op.f("ix_notifications_source_event_id"),
        table_name="notifications",
    )
    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_table("notifications")
    op.execute("DROP TYPE IF EXISTS walletoperationtype;")
