from ..extensions import db
from ..models.seccion import Seccion
from ..models.curso import Curso
from ..models.docente import Docente
from ..models.detalle_matricula import DetalleMatricula


class SeccionService:

    @staticmethod
    def crear_seccion(data):
        curso = Curso.query.get(data["curso_id"])
        if not curso:
            raise ValueError("El curso no existe")

        docente_id = data.get("docente_id")
        if docente_id is not None:
            docente = Docente.query.get(docente_id)
            if not docente:
                raise ValueError("El docente no existe")

        seccion = Seccion(
            curso_id=data["curso_id"],
            docente_id=docente_id,
            periodo_academico_id=data["periodo_academico_id"],
            nombre=data["nombre"],
            aforo=data["aforo"],
        )
        db.session.add(seccion)
        db.session.commit()
        return seccion

    @staticmethod
    def listar_secciones(curso_id=None, docente_id=None, periodo_academico_id=None):
        query = Seccion.query
        if curso_id:
            query = query.filter_by(curso_id=curso_id)
        if docente_id:
            query = query.filter_by(docente_id=docente_id)
        if periodo_academico_id:
            query = query.filter_by(periodo_academico_id=periodo_academico_id)
        return query.all()

    @staticmethod
    def obtener_seccion(seccion_id):
        return Seccion.query.get(seccion_id)

    @staticmethod
    def actualizar_seccion(seccion_id, data):
        """Reasigna docente y/o aforo. Lanza ValueError si el nuevo docente no existe."""
        seccion = Seccion.query.get(seccion_id)
        if not seccion:
            return None

        if data.get("docente_id") is not None:
            docente = Docente.query.get(data["docente_id"])
            if not docente:
                raise ValueError("El docente no existe")
            seccion.docente_id = data["docente_id"]

        if data.get("aforo") is not None:
            seccion.aforo = data["aforo"]

        db.session.commit()
        return seccion

    @staticmethod
    def subir_silabo(seccion_id, silabo_url):
        seccion = Seccion.query.get(seccion_id)
        if not seccion:
            return None
        seccion.silabo_url = silabo_url
        db.session.commit()
        return seccion

    @staticmethod
    def contar_cupos_ocupados(seccion_id):
        return DetalleMatricula.query.filter_by(seccion_id=seccion_id).count()

    @staticmethod
    def eliminar_seccion(seccion_id):
        seccion = Seccion.query.get(seccion_id)
        if not seccion:
            return False
        db.session.delete(seccion)
        db.session.commit()
        return True