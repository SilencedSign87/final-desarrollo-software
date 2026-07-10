from ..extensions import db
from ..models.tipo_documento import TipoDocumento


class TipoDocumentoService:
    @staticmethod
    def listar(solo_activos=False):
        query = TipoDocumento.query
        if solo_activos:
            query = query.filter_by(activo=True)
        return query.order_by(TipoDocumento.nombre.asc()).all()

    @staticmethod
    def obtener(tipo_id):
        return TipoDocumento.query.get(tipo_id)

    @staticmethod
    def obtener_por_nombre(nombre):
        return TipoDocumento.query.filter_by(nombre=nombre).first()

    @staticmethod
    def crear(data):
        existente = TipoDocumento.query.filter_by(nombre=data["nombre"]).first()
        if existente:
            raise ValueError("Ya existe un tipo de documento con ese nombre")

        tipo = TipoDocumento(
            nombre=data["nombre"],
            requiere_pago=data.get("requiere_pago", False),
            activo=data.get("activo", True),
        )
        db.session.add(tipo)
        db.session.commit()
        return tipo

    @staticmethod
    def actualizar(tipo_id, data):
        tipo = TipoDocumento.query.get(tipo_id)
        if not tipo:
            return None

        if "nombre" in data and data["nombre"] is not None:
            conflicto = (
                TipoDocumento.query.filter(
                    TipoDocumento.nombre == data["nombre"],
                    TipoDocumento.id != tipo_id,
                ).first()
            )
            if conflicto:
                raise ValueError("Ya existe un tipo de documento con ese nombre")
            tipo.nombre = data["nombre"]

        if "requiere_pago" in data and data["requiere_pago"] is not None:
            tipo.requiere_pago = data["requiere_pago"]

        if "activo" in data and data["activo"] is not None:
            tipo.activo = data["activo"]

        db.session.commit()
        return tipo

    @staticmethod
    def eliminar(tipo_id):
        tipo = TipoDocumento.query.get(tipo_id)
        if not tipo:
            return False
        db.session.delete(tipo)
        db.session.commit()
        return True
