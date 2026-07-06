from flask_cors import CORS
from .config import Config
from .extensions import db, migrate
from flask_openapi3 import OpenAPI, Info, Tag


def create_app():
    info = Info(
        title="API Sistema Académico",
        description="API del sistema de gestión académica",
        version="1.0.0",
    )

    from .routes.auth import auth_tag

    app = OpenAPI(__name__, info=info, doc_prefix="/docs")
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Registro de modelos
    from .models import (
        User,
        Facultad,
        Especialidad,
        PlanEstudio,
        Curso,
        Estudiante,
        Docente,
        PeriodoAcademico,
        Seccion,
        Horario,
        Matricula,
        DetalleMatricula,
        TipoEvaluacion,
        Evaluacion,
        SolicitudDocumento,
    )

    # Registro de rutas
    from .routes.api import api_bp

    app.register_api(api_bp, url_prefix="/api")

    from .routes.auth import auth_bp

    app.register_api(auth_bp, url_prefix="/api/auth")

    from .routes.matricula import matricula_bp

    app.register_api(matricula_bp, url_prefix="/api/matriculas")

    from .routes.documents import documents_bp

    app.register_api(documents_bp, url_prefix="/api/documentos")

    from .routes.security import security_bp

    app.register_api(security_bp, url_prefix="/api/seguridad")

    return app
