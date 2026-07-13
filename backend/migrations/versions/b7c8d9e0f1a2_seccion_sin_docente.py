"""seccion sin docente

Revision ID: b7c8d9e0f1a2
Revises: e5f6a7b8c9d0
Create Date: 2026-07-12 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b7c8d9e0f1a2"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("seccion", schema=None) as batch_op:
        batch_op.alter_column("docente_id", existing_type=sa.Integer(), nullable=True)


def downgrade():
    with op.batch_alter_table("seccion", schema=None) as batch_op:
        batch_op.alter_column("docente_id", existing_type=sa.Integer(), nullable=False)