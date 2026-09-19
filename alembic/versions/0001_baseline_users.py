"""Baseline: reconoce la tabla users ya existente (creada antes de usar Alembic)

Revision ID: 0001_baseline_users
Revises: 
Create Date: 2026-09-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0001_baseline_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
