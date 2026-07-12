"""codigo ticket correlativo

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-11 22:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    rows = bind.execute(sa.text(f"PRAGMA table_info({table_name})")).fetchall()
    return any(row[1] == column_name for row in rows)


def upgrade():
    bind = op.get_bind()
    # Limpia tabla temporal residual de un intento fallido de batch_alter
    bind.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_solicitud_documento"))

    if not _has_column("solicitud_documento", "codigo_ticket"):
        # SQLite soporta ADD COLUMN directo; evita batch_alter
        op.execute("ALTER TABLE solicitud_documento ADD COLUMN codigo_ticket VARCHAR(30)")
        op.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_solicitud_documento_codigo_ticket "
            "ON solicitud_documento (codigo_ticket)"
        )

    rows = bind.execute(
        sa.text(
            "SELECT id, fecha_creacion FROM solicitud_documento "
            "WHERE codigo_ticket IS NULL ORDER BY id ASC"
        )
    ).fetchall()

    counters = {}
    for row in rows:
        solicitud_id = row[0]
        fecha = row[1]
        if fecha is None:
            year = 2026
        elif hasattr(fecha, "year"):
            year = fecha.year
        else:
            year = int(str(fecha)[:4])
        correlativo = counters.get(year, 0) + 1
        counters[year] = correlativo
        codigo = f"REQ-{year}-{correlativo:04d}"
        bind.execute(
            sa.text(
                "UPDATE solicitud_documento SET codigo_ticket = :codigo WHERE id = :id"
            ),
            {"codigo": codigo, "id": solicitud_id},
        )


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("DROP INDEX IF EXISTS uq_solicitud_documento_codigo_ticket"))
    # SQLite no soporta DROP COLUMN de forma portable en todas las versiones;
    # se deja la columna si no se puede eliminar de forma segura.
