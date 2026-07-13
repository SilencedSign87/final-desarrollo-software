from decimal import Decimal

from ..extensions import db
from ..models.curso import Curso
from ..models.detalle_matricula import DetalleMatricula
from ..models.matricula import Matricula
from ..models.seccion import Seccion
from ..models.estudiante import Estudiante
from ..models.plan_estudio import PlanEstudio
from ..models.periodo_academico import PeriodoAcademico

NOTA_MINIMA_APROBATORIA = Decimal("10.5")


class CursoService:

    @staticmethod
    def obtener_semestre_actual_y_aprobados(estudiante_id):
        aprobados = (
            db.session.query(Curso.id, Curso.semestre_num)
            .join(Seccion, Seccion.curso_id == Curso.id)
            .join(DetalleMatricula, DetalleMatricula.seccion_id == Seccion.id)
            .join(Matricula, Matricula.id == DetalleMatricula.matricula_id)
            .filter(
                Matricula.estudiante_id == estudiante_id,
                DetalleMatricula.promedio_final.isnot(None),
                DetalleMatricula.promedio_final >= NOTA_MINIMA_APROBATORIA,
            )
            .all()
        )

        aprobados_ids = {curso_id for curso_id, _ in aprobados}
        semestre_actual = max((sem for _, sem in aprobados), default=0) + 1
        if semestre_actual < 1:
            semestre_actual = 1

        return semestre_actual, aprobados_ids

    @staticmethod
    def listar_disponibles_para_matricula(estudiante_id):
        estudiante = Estudiante.query.get(estudiante_id)
        if not estudiante:
            raise ValueError("El estudiante no existe")

        semestre_actual, aprobados_ids = (
            CursoService.obtener_semestre_actual_y_aprobados(estudiante_id)
        )

        cursos_plan = Curso.query.filter_by(
            plan_estudios_id=estudiante.plan_estudios_id,
        ).all()

        disponibles = [
            curso
            for curso in cursos_plan
            if curso.id not in aprobados_ids
            and curso.semestre_num <= semestre_actual
            and all(p.id in aprobados_ids for p in curso.prerequisitos)
        ]
        return disponibles, semestre_actual

    @staticmethod
    def crear_curso(data):
        curso = Curso(
            plan_estudios_id=data["plan_estudios_id"],
            nombre=data["nombre"],
            horas_teoria=data["horas_teoria"],
            horas_practica=data["horas_practica"],
            semestre_num=data["semestre_num"],
        )
        db.session.add(curso)
        db.session.flush()

        if data.get("prerequisitos_ids"):
            prerequisitos = Curso.query.filter(
                Curso.id.in_(data["prerequisitos_ids"])
            ).all()
            for prereq in prerequisitos:
                curso.prerequisitos.append(prereq)

        db.session.commit()
        return curso

    @staticmethod
    def listar_cursos(plan_estudios_id=None, semestre_num=None):
        query = Curso.query
        if plan_estudios_id:
            query = query.filter_by(plan_estudios_id=plan_estudios_id)
        if semestre_num:
            query = query.filter_by(semestre_num=semestre_num)
        return query.all()

    @staticmethod
    def obtener_curso(curso_id):
        return Curso.query.get(curso_id)

    @staticmethod
    def actualizar_curso(curso_id, data):
        curso = Curso.query.get(curso_id)
        if not curso:
            return None

        if "nombre" in data and data["nombre"] is not None:
            curso.nombre = data["nombre"]
        if "horas_teoria" in data and data["horas_teoria"] is not None:
            curso.horas_teoria = data["horas_teoria"]
        if "horas_practica" in data and data["horas_practica"] is not None:
            curso.horas_practica = data["horas_practica"]
        if "semestre_num" in data and data["semestre_num"] is not None:
            curso.semestre_num = data["semestre_num"]

        db.session.commit()
        return curso

    @staticmethod
    def eliminar_curso(curso_id):
        curso = Curso.query.get(curso_id)
        if not curso:
            return False
        db.session.delete(curso)
        db.session.commit()
        return True

    @staticmethod
    def listar_planes_estudio():
        """Lista breve de planes de estudio, para selects en el frontend (ej. cumplimiento de plan)."""
        planes = PlanEstudio.query.all()
        return [
            {
                "id": p.id,
                "especialidad_nombre": p.especialidad.nombre,
                "version": p.version,
                "anio": p.anio,
                "estado": p.estado,
            }
            for p in planes
        ]

    @staticmethod
    def cumplimiento_plan_estudios(plan_estudios_id, periodo_academico_id=None):
        plan = PlanEstudio.query.get(plan_estudios_id)
        if not plan:
            raise ValueError("El plan de estudios no existe")

        if periodo_academico_id is None:
            periodo_activo = PeriodoAcademico.query.filter_by(estado="activo").first()
            periodo_academico_id = periodo_activo.id if periodo_activo else None
        if periodo_academico_id is None:
            raise ValueError("No hay un periodo académico activo y no se indicó ninguno")

        cursos = Curso.query.filter_by(plan_estudios_id=plan_estudios_id).order_by(
            Curso.semestre_num, Curso.nombre
        ).all()

        detalle = []
        for curso in cursos:
            secciones = Seccion.query.filter_by(
                curso_id=curso.id, periodo_academico_id=periodo_academico_id
            ).all()

            if not secciones:
                estado = "sin_seccion"
            elif not any(s.docente_id is not None for s in secciones):
                estado = "sin_docente"
            else:
                estado = "cumple"

            detalle.append({
                "curso_id": curso.id,
                "curso_nombre": curso.nombre,
                "semestre_num": curso.semestre_num,
                "total_secciones": len(secciones),
                "estado": estado,
            })

        resumen = {
            "total_cursos": len(detalle),
            "cumple": sum(1 for d in detalle if d["estado"] == "cumple"),
            "sin_docente": sum(1 for d in detalle if d["estado"] == "sin_docente"),
            "sin_seccion": sum(1 for d in detalle if d["estado"] == "sin_seccion"),
        }

        return {
            "plan_estudios_id": plan.id,
            "periodo_academico_id": periodo_academico_id,
            "resumen": resumen,
            "cursos": detalle,
        }