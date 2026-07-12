from ..extensions import db
from ..models.docente import Docente
from ..models.user import User
from ..models.seccion import Seccion
from ..models.periodo_academico import PeriodoAcademico


class DocenteService:

    @staticmethod
    def crear_docente(data):
        user = User.query.get(data["user_id"])
        if not user:
            raise ValueError("El usuario no existe")

        if user.rol != "docente":
            raise ValueError("El usuario no tiene rol 'docente'")

        existente = Docente.query.filter_by(user_id=user.id).first()
        if existente:
            raise ValueError("Este usuario ya tiene un perfil de docente")

        docente = Docente(user_id=user.id, categoria=data["categoria"])
        db.session.add(docente)
        db.session.commit()
        return docente

    @staticmethod
    def listar_docentes():
        return Docente.query.all()

    @staticmethod
    def obtener_docente(docente_id):
        return Docente.query.get(docente_id)

    @staticmethod
    def obtener_docente_por_user_id(user_id):
        return Docente.query.filter_by(user_id=user_id).first()

    @staticmethod
    def actualizar_docente(docente_id, data):
        docente = Docente.query.get(docente_id)
        if not docente:
            return None

        if data.get("categoria") is not None:
            docente.categoria = data["categoria"]

        db.session.commit()
        return docente

    @staticmethod
    def secciones_de_docente(docente_id):
        docente = Docente.query.get(docente_id)
        if not docente:
            return None
        return docente.secciones

    @staticmethod
    def carga_docente(periodo_academico_id=None):
        if periodo_academico_id is None:
            periodo_activo = PeriodoAcademico.query.filter_by(estado="activo").first()
            periodo_academico_id = periodo_activo.id if periodo_activo else None

        docentes = Docente.query.all()
        resultado = []
        for docente in docentes:
            if periodo_academico_id is not None:
                total = Seccion.query.filter_by(
                    docente_id=docente.id, periodo_academico_id=periodo_academico_id
                ).count()
            else:
                total = len(docente.secciones)
            resultado.append({
                "docente_id": docente.id,
                "nombre_completo": f"{docente.user.nombres} {docente.user.apellidos}",
                "categoria": docente.categoria,
                "total_secciones": total,
            })
        return resultado