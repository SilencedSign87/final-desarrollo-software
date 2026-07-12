"""bitacora de auditoria

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-11 23:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auditoria_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("usuario_email", sa.String(length=150), nullable=True),
        sa.Column("accion", sa.String(length=50), nullable=False),
        sa.Column("recurso", sa.String(length=100), nullable=True),
        sa.Column("detalle", sa.String(length=500), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("auditoria_log", schema=None) as batch_op:
        batch_op.create_index("ix_auditoria_log_accion", ["accion"])
        batch_op.create_index("ix_auditoria_log_fecha_creacion", ["fecha_creacion"])


def downgrade():
    with op.batch_alter_table("auditoria_log", schema=None) as batch_op:
        batch_op.drop_index("ix_auditoria_log_fecha_creacion")
        batch_op.drop_index("ix_auditoria_log_accion")
    op.drop_table("auditoria_log")
