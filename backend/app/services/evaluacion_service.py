from decimal import Decimal

from ..extensions import db
from ..models.evaluacion import Evaluacion
from ..models.tipo_evaluacion import TipoEvaluacion
from ..models.matricula import Matricula
from ..models.detalle_matricula import DetalleMatricula
from ..models.seccion import Seccion
from ..models.curso import Curso
from ..models.estudiante import Estudiante
from ..models.periodo_academico import PeriodoAcademico


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

        # Eliminar todas las notas
        Evaluacion.query.filter_by(tipo_evaluacion_id=tipo_evaluacion_id).delete()

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

    @staticmethod
    def validar_promedio(detalle_matricula_id):
        detalle = DetalleMatricula.query.get(detalle_matricula_id)
        if not detalle:
            raise ValueError("El detalle de matrícula no existe")

        tipos = TipoEvaluacion.query.filter_by(seccion_id=detalle.seccion_id).all()
        evaluaciones = Evaluacion.query.filter_by(
            detalle_matricula_id=detalle_matricula_id
        ).all()

        eval_map = {e.tipo_evaluacion_id: e for e in evaluaciones}

        suma_ponderada = Decimal("0")
        suma_pesos = Decimal("0")
        for t in tipos:
            e = eval_map.get(t.id)
            if e and e.nota is not None:
                suma_ponderada += e.nota * t.peso
                suma_pesos += t.peso

        if suma_pesos > 0:
            promedio = (suma_ponderada / suma_pesos).quantize(Decimal("0.00"))
        else:
            promedio = None

        detalle.promedio_final = promedio
        db.session.commit()
        return float(promedio) if promedio else None

    @staticmethod
    def listar_notas_por_seccion(seccion_id):
        from ..models import Matricula, Estudiante, User

        # Tipos de evaluación de la sección
        tipos = TipoEvaluacion.query.filter_by(seccion_id=seccion_id).all()

        # if not tipos:
        #     return {"tipos_evaluacion": [], "estudiantes": []}

        # Detalles de matrícula de la sección con datos del estudiante
        detalles = (
            db.session.query(
                DetalleMatricula.id,
                Estudiante.id,
                User.nombres,
                User.apellidos,
                DetalleMatricula.promedio_final,
            )
            .join(Matricula, Matricula.id == DetalleMatricula.matricula_id)
            .join(Estudiante, Estudiante.id == Matricula.estudiante_id)
            .join(User, User.id == Estudiante.user_id)
            .filter(DetalleMatricula.seccion_id == seccion_id)
            .all()
        )

        detalle_ids = [d[0] for d in detalles]
        tipo_ids = [t.id for t in tipos]

        # Evaluaciones existentes → lookup (detalle_id, tipo_id) -> evaluacion
        evaluaciones = Evaluacion.query.filter(
            Evaluacion.detalle_matricula_id.in_(detalle_ids),
            Evaluacion.tipo_evaluacion_id.in_(tipo_ids),
        ).all()

        eval_map: dict[tuple[int, int], Evaluacion] = {
            (e.detalle_matricula_id, e.tipo_evaluacion_id): e for e in evaluaciones
        }

        estudiantes = []
        for detalle_id, est_id, nombres, apellidos, promedio in detalles:
            notas = []
            suma_ponderada = Decimal("0")
            suma_pesos = Decimal("0")

            for t in tipos:
                e = eval_map.get((detalle_id, t.id))
                nota_valor = e.nota if e else None
                notas.append(
                    {
                        "tipo_evaluacion_id": t.id,
                        "evaluacion_id": e.id if e else None,
                        "nota": nota_valor,
                    }
                )
                if nota_valor is not None:
                    suma_ponderada += nota_valor * t.peso
                    suma_pesos += t.peso

            promedio_calculado = (
                (suma_ponderada / suma_pesos).quantize(Decimal("0.00"))
                if suma_pesos > 0
                else None
            )

            estudiantes.append(
                {
                    "detalle_matricula_id": detalle_id,
                    "estudiante_id": est_id,
                    "estudiante_nombre": f"{nombres} {apellidos}",
                    "notas": notas,
                    "promedio_final": promedio or promedio_calculado,
                }
            )

        return {
            "tipos_evaluacion": [
                {
                    "id": t.id,
                    "seccion_id": t.seccion_id,
                    "nombre": t.nombre,
                    "peso": t.peso,
                }
                for t in tipos
            ],
            "estudiantes": estudiantes,
        }

    @staticmethod
    def listar_notas_estudiante(id_estudiante, periodo_academico_id):
    
        matricula = Matricula.query.filter_by(
            estudiante_id=id_estudiante, periodo_academico_id=periodo_academico_id
        ).first()

        if not matricula:
            return []

        detalles = (
            db.session.query(DetalleMatricula, Seccion, Curso)
            .join(Seccion, Seccion.id == DetalleMatricula.seccion_id)
            .join(Curso, Curso.id == Seccion.curso_id)
            .filter(DetalleMatricula.matricula_id == matricula.id)
            .all()
        )
        result = []
        for detalle, seccion, curso in detalles:
            tipos = TipoEvaluacion.query.filter_by(seccion_id=seccion.id).all()
            evaluaciones = Evaluacion.query.filter_by(detalle_matricula_id=detalle.id).all()

            eval_map = {e.tipo_evaluacion_id: e for e in evaluaciones}

            evaluaciones_list = [
                {
                    "nombre": t.nombre,
                    "nota": (
                        float(eval_map[t.id].nota) if t.id in eval_map else Decimal("0")
                    ),
                    "peso": float(t.peso),
                }
                for t in tipos
            ]

            result.append(
                {
                    "curso": curso.nombre,
                    "seccion": seccion.nombre,
                    "promedio": (
                        float(detalle.promedio_final) if detalle.promedio_final else None
                    ),
                    "evaluaciones": evaluaciones_list,
                }
            )

        return result
