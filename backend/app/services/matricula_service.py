from ..extensions import db
from ..models.matricula import Matricula
from ..models.detalle_matricula import DetalleMatricula
from ..models.seccion import Seccion
from ..models.estudiante import Estudiante


class MatriculaService:

    @staticmethod
    def crear_matricula(estudiante_id, data):
        """
        Crea una matrícula en estado 'pendiente' junto con sus detalles.
        Valida que las secciones existan y tengan cupo disponible antes de confirmar.
        Lanza ValueError con un mensaje claro si algo no cumple.
        """
        secciones = Seccion.query.filter(
            Seccion.id.in_(data["secciones_ids"])
        ).all()

        if len(secciones) != len(data["secciones_ids"]):
            raise ValueError("Una o más secciones no existen")

        for seccion in secciones:
            ya_matriculados = DetalleMatricula.query.filter_by(
                seccion_id=seccion.id
            ).count()
            if ya_matriculados >= seccion.aforo:
                raise ValueError(
                    f"La sección '{seccion.nombre}' ya no tiene cupos disponibles"
                )

        matricula = Matricula(
            periodo_academico_id=data["periodo_academico_id"],
            estudiante_id=estudiante_id,
            estado="pendiente",
            comprobante_url=data["comprobante_url"],
        )
        db.session.add(matricula)
        db.session.flush()

        for seccion in secciones:
            detalle = DetalleMatricula(
                matricula_id=matricula.id,
                seccion_id=seccion.id,
                estado_curso="matriculado",
            )
            db.session.add(detalle)

        db.session.commit()
        return matricula

    @staticmethod
    def listar_matriculas(estado=None):
        query = Matricula.query
        if estado:
            query = query.filter_by(estado=estado)
        return query.all()

    @staticmethod
    def obtener_matricula(matricula_id):
        return Matricula.query.get(matricula_id)

    @staticmethod
    def validar_matricula(matricula_id, admin_user_id, data):
        matricula = Matricula.query.get(matricula_id)
        if not matricula:
            return None

        matricula.estado = data["estado"]
        matricula.observacion = data.get("observacion")
        matricula.validado_user_id = admin_user_id

        db.session.commit()
        return matricula

    @staticmethod
    def obtener_estudiante_por_user_id(user_id):
        return Estudiante.query.filter_by(user_id=user_id).first()

    @staticmethod
    def estadisticas():
        """Conteo de matrículas agrupado por estado"""
        resultados = (
            db.session.query(Matricula.estado, db.func.count(Matricula.id))
            .group_by(Matricula.estado)
            .all()
        )
        return {estado: total for estado, total in resultados}