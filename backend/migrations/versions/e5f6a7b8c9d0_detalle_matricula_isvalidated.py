"""add is_validated to detalle_matricula

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-12 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("detalle_matricula", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_validated",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade():
    with op.batch_alter_table("detalle_matricula", schema=None) as batch_op:
        batch_op.drop_column("is_validated")
