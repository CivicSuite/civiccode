"""Add durable CivicClerk handoff resolution fields."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "civiccode_0010_handoff_resolve"
down_revision = "civiccode_0009_operational_state"
branch_labels = None
depends_on = None


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {item["name"] for item in inspector.get_columns(table_name, schema="civiccode")}
    if column.name not in existing:
        op.add_column(table_name, column, schema="civiccode")


def upgrade() -> None:
    _add_column_if_missing(
        "ordinance_handoff_records",
        sa.Column("resolved_section_version_id", sa.String(255), nullable=True),
    )
    _add_column_if_missing(
        "ordinance_handoff_records",
        sa.Column("resolved_by", sa.String(255), nullable=True),
    )
    _add_column_if_missing(
        "ordinance_handoff_records",
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ordinance_handoff_records", "resolved_at", schema="civiccode")
    op.drop_column("ordinance_handoff_records", "resolved_by", schema="civiccode")
    op.drop_column("ordinance_handoff_records", "resolved_section_version_id", schema="civiccode")
