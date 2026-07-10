from flask import app
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

    # Comandos
    @app.cli.command("seed")
    def seed_command():
        """Crea usuarios por defecto si no existen."""
        from .seed import seed_default_users, seed_test_data
        seed_default_users()
        seed_test_data()


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
        TipoDocumento,
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

    from .routes.curso import curso_bp

    app.register_api(curso_bp, url_prefix="/api/cursos")

    from .routes.docente import docente_bp

    app.register_api(docente_bp, url_prefix="/api/docentes")
    
    from .routes.seccion import seccion_bp

    app.register_api(seccion_bp, url_prefix="/api/secciones")

    from .routes.horario import horario_bp

    app.register_api(horario_bp, url_prefix="/api/horarios")

    from .routes.periodo_academico import periodo_academico_bp
    
    app.register_api(periodo_academico_bp, url_prefix="/api/periodos-academicos")

    from .routes.evaluaciones import evaluaciones_bp
    
    app.register_api(evaluaciones_bp, url_prefix="/api/evaluaciones")

    from .routes.tipo_documento import tipo_documento_bp

    app.register_api(tipo_documento_bp, url_prefix="/api/tipos-documento")

    return app
