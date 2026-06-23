"""add outbox events

Revision ID: 4d3f6d9a7c12
Revises: d760d17516d9
Create Date: 2026-06-23 13:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4d3f6d9a7c12"
down_revision: Union[str, Sequence[str], None] = "d760d17516d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    outbox_status = sa.Enum(
        "PENDING",
        "FAILED",
        "PUBLISHED",
        "DEAD_LETTER",
        name="outboxstatus",
    )
    outbox_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("aggregate_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("next_retry_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_error_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "status",
            outbox_status,
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("max_retries", sa.Integer(), server_default="3", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_outbox_events_aggregate_id"),
        "outbox_events",
        ["aggregate_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_events_created_at"),
        "outbox_events",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_events_event_type"),
        "outbox_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_events_next_retry_at"),
        "outbox_events",
        ["next_retry_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_events_published_at"),
        "outbox_events",
        ["published_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_events_status"),
        "outbox_events",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_outbox_events_status"), table_name="outbox_events")
    op.drop_index(op.f("ix_outbox_events_published_at"), table_name="outbox_events")
    op.drop_index(op.f("ix_outbox_events_next_retry_at"), table_name="outbox_events")
    op.drop_index(op.f("ix_outbox_events_event_type"), table_name="outbox_events")
    op.drop_index(op.f("ix_outbox_events_created_at"), table_name="outbox_events")
    op.drop_index(op.f("ix_outbox_events_aggregate_id"), table_name="outbox_events")
    op.drop_table("outbox_events")
    op.execute("DROP TYPE IF EXISTS outboxstatus;")
