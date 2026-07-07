from ..extensions import db
from ..models.curso import Curso


class CursoService:

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