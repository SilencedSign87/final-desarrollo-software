from flask import g

from ..extensions import db
from ..models.auditoria_log import AuditoriaLog
from ..utils.datetime_utils import utc_now_naive


class AuditService:
    """Registra eventos críticos en bitácora (solo escritura)."""

    @staticmethod
    def log(accion: str, detalle: str, recurso: str | None = None, user=None):
        actor = user
        if actor is None:
            actor = getattr(g, "current_user", None)

        entry = AuditoriaLog(
            user_id=actor.id if actor else None,
            usuario_email=actor.email if actor else None,
            accion=accion,
            recurso=recurso,
            detalle=detalle[:500],
            fecha_creacion=utc_now_naive(),
        )
        db.session.add(entry)
        # El commit lo hace el caller para mantener la transacción

    @staticmethod
    def list_logs(page: int = 1, per_page: int = 15, accion: str | None = None):
        query = AuditoriaLog.query
        if accion:
            query = query.filter_by(accion=accion)
        return query.order_by(AuditoriaLog.fecha_creacion.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    @staticmethod
    def list_role_changes(page: int = 1, per_page: int = 15):
        return AuditService.list_logs(page=page, per_page=per_page, accion="cambio_rol")
