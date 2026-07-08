from ..extensions import db
from ..models.evaluacion import Evaluacion
from ..models.tipo_evaluacion import TipoEvaluacion
from ..models.detalle_matricula import DetalleMatricula
from ..models.seccion import Seccion


class TipoEvaluacionService:

    @staticmethod
    def crear_tipo_evaluacion(data):
        seccion = Seccion.query.get(data["seccion_id"])
        if not seccion:
            raise ValueError("La sección no existe")

        tipo = TipoEvaluacion(
            seccion_id=data["seccion_id"],
            nombre=data["nombre"],
            peso=data["peso"],
        )
        db.session.add(tipo)
        db.session.commit()
        return tipo

    @staticmethod
    def obtener_tipo_evaluacion(tipo_evaluacion_id):
        return TipoEvaluacion.query.get(tipo_evaluacion_id)

    @staticmethod
    def actualizar_tipo_evaluacion(tipo_evaluacion_id, data):
        tipo = TipoEvaluacion.query.get(tipo_evaluacion_id)
        if not tipo:
            return None
        if data.get("nombre") is not None:
            tipo.nombre = data["nombre"]
        if data.get("peso") is not None:
            tipo.peso = data["peso"]
        db.session.commit()
        return tipo

    @staticmethod
    def eliminar_tipo_evaluacion(tipo_evaluacion_id):
        tipo = TipoEvaluacion.query.get(tipo_evaluacion_id)
        if not tipo:
            return False
        db.session.delete(tipo)
        db.session.commit()
        return True

    @staticmethod
    def listar_tipos_evaluacion(seccion_id=None, nombre=None, evaluacion_id=None):
        query = TipoEvaluacion.query
        if seccion_id is not None:
            query = query.filter_by(seccion_id=seccion_id)
        if nombre:
            query = query.filter(TipoEvaluacion.nombre.ilike(f"%{nombre}%"))
        if evaluacion_id is not None:
            query = query.join(TipoEvaluacion.evaluaciones).filter(
                Evaluacion.id == evaluacion_id
            )
        return query.all()


class EvaluacionService:

    @staticmethod
    def crear_evaluacion(data):
        tipo = TipoEvaluacion.query.get(data["tipo_evaluacion_id"])
        if not tipo:
            raise ValueError("El tipo de evaluación no existe")

        detalle = DetalleMatricula.query.get(data["detalle_matricula_id"])
        if not detalle:
            raise ValueError("El detalle de matrícula no existe")

        evaluacion = Evaluacion(
            tipo_evaluacion_id=data["tipo_evaluacion_id"],
            detalle_matricula_id=data["detalle_matricula_id"],
            nota=data["nota"],
        )
        db.session.add(evaluacion)
        db.session.commit()
        return evaluacion

    @staticmethod
    def listar_evaluaciones(tipo_evaluacion_id=None, detalle_matricula_id=None):
        query = Evaluacion.query
        if tipo_evaluacion_id is not None:
            query = query.filter_by(tipo_evaluacion_id=tipo_evaluacion_id)
        if detalle_matricula_id is not None:
            query = query.filter_by(detalle_matricula_id=detalle_matricula_id)
        return query.all()

    @staticmethod
    def obtener_evaluacion(evaluacion_id):
        return Evaluacion.query.get(evaluacion_id)

    @staticmethod
    def actualizar_evaluacion(evaluacion_id, data):
        evaluacion = Evaluacion.query.get(evaluacion_id)
        if not evaluacion:
            return None
        if data.get("nota") is not None:
            evaluacion.nota = data["nota"]
        db.session.commit()
        return evaluacion

    @staticmethod
    def eliminar_evaluacion(evaluacion_id):
        evaluacion = Evaluacion.query.get(evaluacion_id)
        if not evaluacion:
            return False
        db.session.delete(evaluacion)
        db.session.commit()
        return True

    @staticmethod
    def obtener_estudiante(evaluacion_id):
        evaluacion = Evaluacion.query.get(evaluacion_id)
        if not evaluacion:
            return None
        detalle = evaluacion.detalle_matricula
        if not detalle:
            return None
        return detalle.matricula.estudiante
