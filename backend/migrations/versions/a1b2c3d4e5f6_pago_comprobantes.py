"""pago y comprobantes

Revision ID: a1b2c3d4e5f6
Revises: 7e1a406e5b99
Create Date: 2026-07-10 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "7e1a406e5b99"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tipo_documento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("requiere_pago", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )

    with op.batch_alter_table("periodo_academico", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "requiere_pago",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    with op.batch_alter_table("solicitud_documento", schema=None) as batch_op:
        batch_op.add_column(sa.Column("tipo_documento_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("comprobante_url", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column(
                "requiere_pago",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.create_foreign_key(
            "fk_solicitud_documento_tipo_documento",
            "tipo_documento",
            ["tipo_documento_id"],
            ["id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
        )


def downgrade():
    with op.batch_alter_table("solicitud_documento", schema=None) as batch_op:
        batch_op.drop_constraint("fk_solicitud_documento_tipo_documento", type_="foreignkey")
        batch_op.drop_column("requiere_pago")
        batch_op.drop_column("comprobante_url")
        batch_op.drop_column("tipo_documento_id")

    with op.batch_alter_table("periodo_academico", schema=None) as batch_op:
        batch_op.drop_column("requiere_pago")

    op.drop_table("tipo_documento")
