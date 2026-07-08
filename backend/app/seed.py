from datetime import datetime, time
from werkzeug.security import generate_password_hash

from .extensions import db
from .models.user import User
from .models.facultad import Facultad
from .models.especialidad import Especialidad
from .models.plan_estudio import PlanEstudio
from .models.curso import Curso
from .models.periodo_academico import PeriodoAcademico
from .models.docente import Docente
from .models.seccion import Seccion
from .models.estudiante import Estudiante
from .models.horario import Horario

def _safe_add(entity, desc="entidad"):
    try:
        with db.session.begin_nested():
            db.session.add(entity)
        return entity
    except Exception as e:
        print(f"  [SKIP] {desc}: {e}")
        return None

def seed_default_users():
    if User.query.first() is not None:
        return  # Ya hay usuarios

    default_users = [
        {
            "nombres": "Admin",
            "apellidos": "Sistema",
            "rol": "administrador",
            "dni": "00000000",
            "email": "admin@sistema.edu",
            "password": generate_password_hash("admin123"),
        },
        {
            "nombres": "Director",
            "apellidos": "Academico",
            "rol": "direccion",
            "dni": "11111111",
            "email": "director@sistema.edu",
            "password": generate_password_hash("director123"),
        },
        {
            "nombres": "Docente",
            "apellidos": "Ejemplo",
            "rol": "docente",
            "dni": "22222222",
            "email": "docente@sistema.edu",
            "password": generate_password_hash("docente123"),
        },
        {
            "nombres": "Estudiante",
            "apellidos": "Ejemplo",
            "rol": "estudiante",
            "dni": "33333333",
            "email": "estudiante@sistema.edu",
            "password": generate_password_hash("estudiante123"),
        },
    ]

    for user_data in default_users:
        _safe_add(User(**user_data), f"Usuario {user_data['email']}")

    db.session.commit()
    print("[SYSTEM] Usuarios por defecto creados exitosamente.")

def seed_test_data():
    print("[SEED] Insertando datos de prueba...")

    # ── 1. Facultad ─────────────────────────────
    facultad = _safe_add(
        Facultad(nombre="Ingeniería de Sistemas"),
        "Facultad",
    )
    if not facultad:
        print("[ERROR] No se pudo crear la Facultad. Abortando.")
        return

    # ── 2. Especialidad ─────────────────────────
    especialidad = _safe_add(
        Especialidad(
            facultad_id=facultad.id,
            nombre="Sistemas",
            modalidad="presencial",
        ),
        "Especialidad",
    )
    if not especialidad:
        print("[ERROR] No se pudo crear la Especialidad. Abortando.")
        return

    # ── 3. Plan de Estudio ──────────────────────
    plan = _safe_add(
        PlanEstudio(
            especialidad_id=especialidad.id,
            version="2024",
            anio=2024,
            estado="activo",
        ),
        "PlanEstudio",
    )
    if not plan:
        print("[ERROR] No se pudo crear el PlanEstudio. Abortando.")
        return

    # ── 4. Curso ────────────────────────────────
    curso = _safe_add(
        Curso(
            plan_estudios_id=plan.id,
            nombre="Desarrollo de Aplicaciones Web",
            horas_teoria=3,
            horas_practica=4,
            semestre_num=9,
        ),
        "Curso",
    )
    if not curso:
        print("[ERROR] No se pudo crear el Curso. Abortando.")
        return

    # ── 5. Periodo Académico ────────────────────
    periodo = _safe_add(
        PeriodoAcademico(
            semestre="2026-I",
            fecha_inicio=datetime(2026, 3, 1),
            fecha_fin=datetime(2026, 7, 15),
            estado="activo",
        ),
        "PeriodoAcademico",
    )
    if not periodo:
        print("[ERROR] No se pudo crear el PeriodoAcademico. Abortando.")
        return

    # ── 6. Usuario docente + perfil Docente ─────
    user_docente = _safe_add(
        User(
            nombres="Carlos",
            apellidos="Ramírez",
            email="docente.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="docente",
            dni="12345678",
        ),
        "Usuario docente",
    )

    docente = None
    if user_docente:
        docente = _safe_add(
            Docente(user_id=user_docente.id, categoria="asociado"),
            "Docente",
        )

    # ── 7. Sección ──────────────────────────────
    seccion = None
    if curso and docente and periodo:
        seccion = _safe_add(
            Seccion(
                curso_id=curso.id,
                docente_id=docente.id,
                periodo_academico_id=periodo.id,
                nombre="DAW-A",
                aforo=30,
            ),
            "Sección",
        )

    # ── 8. Horario ──────────────────────────────
    if seccion:
        _safe_add(
            Horario(
                seccion_id=seccion.id,
                dia_semana=0,
                hora_inicio=time(8, 0),
                hora_final=time(10, 0),
                aula="Lab-201",
            ),
            "Horario",
        )

    # ── 9. Usuarios estudiantes + perfiles ──────
    estudiantes_data = [
        {
            "nombres": "José",
            "apellidos": "Araujo",
            "email": "estudiante.prueba@uncp.edu.pe",
            "password": generate_password_hash("123456"),
            "rol": "estudiante",
            "dni": "87654321",
        },
        {
            "nombres": "María",
            "apellidos": "Torres",
            "email": "estudiante2.prueba@uncp.edu.pe",
            "password": generate_password_hash("123456"),
            "rol": "estudiante",
            "dni": "55667788",
        },
    ]

    for data in estudiantes_data:
        user_est = _safe_add(User(**data), f"Usuario {data['email']}")
        if user_est and plan:
            _safe_add(
                Estudiante(user_id=user_est.id, plan_estudios_id=plan.id),
                f"Estudiante {data['email']}",
            )

    # ── 10. Usuario admin de prueba ─────────────
    _safe_add(
        User(
            nombres="Admin",
            apellidos="Prueba",
            email="admin.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="administrador",
            dni="11223344",
        ),
        "Usuario admin de prueba",
    )

    # ── 11. Usuario dirección de prueba ─────────
    _safe_add(
        User(
            nombres="Directora",
            apellidos="Prueba",
            email="direccion.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="direccion",
            dni="99887766",
        ),
        "Usuario dirección de prueba",
    )

    # ── Persistir todo lo que sí funcionó ─────
    db.session.commit()
    print("[SEED] Datos de prueba insertados correctamente.")