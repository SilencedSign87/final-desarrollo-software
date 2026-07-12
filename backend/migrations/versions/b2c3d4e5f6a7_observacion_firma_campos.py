"""observacion y campos de firma

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-11 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("solicitud_documento", schema=None) as batch_op:
        batch_op.add_column(sa.Column("observacion", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("adjunto_autorizacion_url", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("respondido_por_user_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("fecha_respuesta", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("fecha_emision", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("firma_digital", sa.String(length=512), nullable=True))
        batch_op.add_column(sa.Column("firma_algoritmo", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("firma_huella_cert", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("contenido_hash", sa.String(length=128), nullable=True))


def downgrade():
    with op.batch_alter_table("solicitud_documento", schema=None) as batch_op:
        batch_op.drop_column("contenido_hash")
        batch_op.drop_column("firma_huella_cert")
        batch_op.drop_column("firma_algoritmo")
        batch_op.drop_column("firma_digital")
        batch_op.drop_column("fecha_emision")
        batch_op.drop_column("fecha_respuesta")
        batch_op.drop_column("respondido_por_user_id")
        batch_op.drop_column("adjunto_autorizacion_url")
        batch_op.drop_column("observacion")
