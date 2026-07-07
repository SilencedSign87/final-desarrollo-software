from ..extensions import db
from ..models.docente import Docente
from ..models.user import User


class DocenteService:

    @staticmethod
    def crear_docente(data):
        """
        Crea el perfil de Docente para un usuario ya registrado.
        Lanza ValueError si el usuario no existe, si no tiene rol 'docente',
        o si ya tiene un perfil de docente creado.
        """
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
    def carga_docente():
        """
        Para dirección: cuenta cuántas secciones tiene asignadas cada docente.
        Devuelve una lista de dicts con el nombre completo del docente y su carga.
        """
        docentes = Docente.query.all()
        resultado = []
        for docente in docentes:
            resultado.append({
                "docente_id": docente.id,
                "nombre_completo": f"{docente.user.nombres} {docente.user.apellidos}",
                "categoria": docente.categoria,
                "total_secciones": len(docente.secciones),
            })
        return resultado