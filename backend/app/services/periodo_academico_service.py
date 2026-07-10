from datetime import datetime

from ..extensions import db
from ..models.periodo_academico import PeriodoAcademico
from ..models.seccion import Seccion
from ..models.estudiante import Estudiante
from ..models.curso import Curso
from ..models.matricula import Matricula


class PeriodoAcademicoService:

    @staticmethod
    def _normalize(data):
        payload = dict(data)
        for key in ("fecha_inicio", "fecha_fin"):
            value = payload.get(key)
            if isinstance(value, str):
                payload[key] = datetime.fromisoformat(value)
        return payload

    @staticmethod
    def search(query):
        q = PeriodoAcademico.query

        if query.semestre is not None:
            q = q.filter_by(semestre=query.semestre)

        if query.estado is not None:
            q = q.filter_by(estado=query.estado)

        return q.all()

    @staticmethod
    def get_by_id(periodo_id):
        return PeriodoAcademico.query.get(periodo_id)

    @staticmethod
    def create(data):
        periodo = PeriodoAcademico(**PeriodoAcademicoService._normalize(data))
        db.session.add(periodo)
        db.session.commit()
        return periodo

    @staticmethod
    def update(periodo_id, data):
        periodo = PeriodoAcademico.query.get(periodo_id)
        if not periodo:
            return None
        payload = PeriodoAcademicoService._normalize(data)
        for key, value in payload.items():
            if value is not None:
                setattr(periodo, key, value)
        db.session.commit()
        return periodo

    @staticmethod
    def delete(periodo_id):
        periodo = PeriodoAcademico.query.get(periodo_id)
        if not periodo:
            return False
        db.session.delete(periodo)
        db.session.commit()
        return True

    @staticmethod
    def get_cursos_by_periodo(periodo_id):
        periodo = PeriodoAcademico.query.get(periodo_id)
        if not periodo:
            return None

        # Obtener cursos únicos a través de las secciones del periodo
        cursos = (
            Curso.query
            .join(Seccion, Seccion.curso_id == Curso.id)
            .filter(Seccion.periodo_academico_id == periodo_id)
            .distinct()
            .all()
        )
        return cursos
    
    def get_periodos_academicos_estudiante(estudiante_user_id):
        estudiante = Estudiante.query.filter_by(user_id=estudiante_user_id).first()
        
        if not estudiante:
            return None
        
        periodos_matriculados = PeriodoAcademico.query.join(Matricula).filter(Matricula.estudiante_id == estudiante.id).all()
        
        return periodos_matriculados
