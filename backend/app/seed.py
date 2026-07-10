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
from .models.tipo_documento import TipoDocumento


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

    # ── 4. Cursos ───────────────────────────────
    cursos_data = [
        # Semestre 1
        {"nombre": "Matemática Básica", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 1},
        {"nombre": "Introducción a la Programación", "horas_teoria": 2, "horas_practica": 4, "semestre_num": 1},
        {"nombre": "Comunicación Oral y Escrita", "horas_teoria": 2, "horas_practica": 2, "semestre_num": 1},
        # Semestre 2
        {"nombre": "Cálculo Diferencial", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 2},
        {"nombre": "Programación Orientada a Objetos", "horas_teoria": 2, "horas_practica": 4, "semestre_num": 2},
        {"nombre": "Estructuras Discretas", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 2},
        # Semestre 3
        {"nombre": "Estructura de Datos", "horas_teoria": 2, "horas_practica": 4, "semestre_num": 3},
        {"nombre": "Base de Datos I", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 3},
        {"nombre": "Arquitectura de Computadoras", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 3},
        # Semestre 4
        {"nombre": "Algoritmos y Complejidad", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 4},
        {"nombre": "Base de Datos II", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 4},
        {"nombre": "Sistemas Operativos", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 4},
        # Semestre 5
        {"nombre": "Ingeniería de Software I", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 5},
        {"nombre": "Redes de Computadoras", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 5},
        {"nombre": "Análisis y Diseño de Sistemas", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 5},
        # Semestre 6
        {"nombre": "Ingeniería de Software II", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 6},
        {"nombre": "Desarrollo de Aplicaciones Móviles", "horas_teoria": 2, "horas_practica": 4, "semestre_num": 6},
        {"nombre": "Inteligencia Artificial", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 6},
        # Semestre 7
        {"nombre": "Gestión de Proyectos de Software", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 7},
        {"nombre": "Seguridad Informática", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 7},
        {"nombre": "Computación en la Nube", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 7},
        # Semestre 8
        {"nombre": "Arquitectura de Software", "horas_teoria": 3, "horas_practica": 2, "semestre_num": 8},
        {"nombre": "Machine Learning", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 8},
        {"nombre": "Internet de las Cosas", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 8},
        # Semestre 9
        {"nombre": "Desarrollo de Aplicaciones Web", "horas_teoria": 3, "horas_practica": 4, "semestre_num": 9},
        {"nombre": "Taller de Tesis I", "horas_teoria": 2, "horas_practica": 2, "semestre_num": 9},
        {"nombre": "Calidad de Software", "horas_teoria": 2, "horas_practica": 3, "semestre_num": 9},
        # Semestre 10
        {"nombre": "Taller de Tesis II", "horas_teoria": 2, "horas_practica": 2, "semestre_num": 10},
        {"nombre": "Ética Profesional", "horas_teoria": 2, "horas_practica": 1, "semestre_num": 10},
        {"nombre": "Prácticas Preprofesionales", "horas_teoria": 1, "horas_practica": 4, "semestre_num": 10},
    ]

    cursos = {}
    for c in cursos_data:
        curso = _safe_add(
            Curso(plan_estudios_id=plan.id, **c),
            f"Curso {c['nombre']}",
        )
        if curso:
            cursos[c["nombre"]] = curso

    if not cursos:
        print("[ERROR] No se pudo crear ningún Curso. Abortando.")
        return

    # ── 5. Periodos Académicos ──────────────────
    periodos_data = [
        {
            "semestre": "2025-I",
            "fecha_inicio": datetime(2025, 3, 3),
            "fecha_fin": datetime(2025, 7, 18),
            "estado": "cerrado",
            "requiere_pago": True,
        },
        {
            "semestre": "2025-II",
            "fecha_inicio": datetime(2025, 8, 18),
            "fecha_fin": datetime(2025, 12, 19),
            "estado": "cerrado",
            "requiere_pago": True,
        },
        {
            "semestre": "2026-I",
            "fecha_inicio": datetime(2026, 3, 1),
            "fecha_fin": datetime(2026, 7, 15),
            "estado": "activo",
            "requiere_pago": True,
        },
        {
            "semestre": "2026-II",
            "fecha_inicio": datetime(2026, 8, 17),
            "fecha_fin": datetime(2026, 12, 18),
            "estado": "planificado",
            "requiere_pago": False,
        },
    ]

    periodos = {}
    for p in periodos_data:
        periodo = _safe_add(
            PeriodoAcademico(**p),
            f"Periodo {p['semestre']}",
        )
        if periodo:
            periodos[p["semestre"]] = periodo

    periodo_activo = periodos.get("2026-I")
    if not periodo_activo:
        print("[ERROR] No se pudo crear el PeriodoAcademico activo. Abortando.")
        return

    # ── 6. Docentes (@sistema.edu) ───────────────
    # Incluye el usuario por defecto docente@sistema.edu + docentes adicionales
    docentes_data = [
        {
            "nombres": "Docente",
            "apellidos": "Ejemplo",
            "email": "docente@sistema.edu",
            "dni": "22222222",
            "password": "docente123",
            "categoria": "asociado",
        },
        {
            "nombres": "Carlos",
            "apellidos": "Ramírez",
            "email": "carlos.ramirez@sistema.edu",
            "dni": "12345678",
            "password": "123456",
            "categoria": "asociado",
        },
        {
            "nombres": "Ana",
            "apellidos": "Mendoza",
            "email": "ana.mendoza@sistema.edu",
            "dni": "23456789",
            "password": "123456",
            "categoria": "principal",
        },
        {
            "nombres": "Luis",
            "apellidos": "Vargas",
            "email": "luis.vargas@sistema.edu",
            "dni": "34567890",
            "password": "123456",
            "categoria": "auxiliar",
        },
        {
            "nombres": "Patricia",
            "apellidos": "Quispe",
            "email": "patricia.quispe@sistema.edu",
            "dni": "45678901",
            "password": "123456",
            "categoria": "asociado",
        },
        {
            "nombres": "Roberto",
            "apellidos": "Huamán",
            "email": "roberto.huaman@sistema.edu",
            "dni": "56789012",
            "password": "123456",
            "categoria": "principal",
        },
    ]

    docentes = []
    for d in docentes_data:
        user_doc = User.query.filter_by(email=d["email"]).first()
        if not user_doc:
            user_doc = _safe_add(
                User(
                    nombres=d["nombres"],
                    apellidos=d["apellidos"],
                    email=d["email"],
                    password=generate_password_hash(d["password"]),
                    rol="docente",
                    dni=d["dni"],
                ),
                f"Usuario docente {d['email']}",
            )
        if user_doc:
            docente = Docente.query.filter_by(user_id=user_doc.id).first()
            if not docente:
                docente = _safe_add(
                    Docente(user_id=user_doc.id, categoria=d["categoria"]),
                    f"Docente {d['email']}",
                )
            if docente:
                docentes.append(docente)

    if not docentes:
        print("[ERROR] No se pudo crear ningún Docente. Abortando.")
        return

    # ── 7. Secciones + Horarios (periodo activo) ─
    # dia_semana: 0=lunes ... 5=sábado
    secciones_data = [
        {
            "curso": "Desarrollo de Aplicaciones Web",
            "nombre": "DAW-A",
            "aforo": 30,
            "docente_idx": 0,
            "horarios": [
                {"dia_semana": 0, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Lab-201"},
                {"dia_semana": 2, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Lab-201"},
            ],
        },
        {
            "curso": "Desarrollo de Aplicaciones Web",
            "nombre": "DAW-B",
            "aforo": 28,
            "docente_idx": 1,
            "horarios": [
                {"dia_semana": 1, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Lab-202"},
                {"dia_semana": 3, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Lab-202"},
            ],
        },
        {
            "curso": "Base de Datos I",
            "nombre": "BD1-A",
            "aforo": 35,
            "docente_idx": 2,
            "horarios": [
                {"dia_semana": 0, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Aula-105"},
                {"dia_semana": 2, "hora_inicio": time(14, 0), "hora_final": time(16, 0), "aula": "Lab-203"},
            ],
        },
        {
            "curso": "Base de Datos II",
            "nombre": "BD2-A",
            "aforo": 32,
            "docente_idx": 3,
            "horarios": [
                {"dia_semana": 1, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Aula-110"},
                {"dia_semana": 4, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Lab-204"},
            ],
        },
        {
            "curso": "Estructura de Datos",
            "nombre": "ED-A",
            "aforo": 40,
            "docente_idx": 3,
            "horarios": [
                {"dia_semana": 0, "hora_inicio": time(14, 0), "hora_final": time(16, 0), "aula": "Lab-205"},
                {"dia_semana": 3, "hora_inicio": time(14, 0), "hora_final": time(16, 0), "aula": "Lab-205"},
            ],
        },
        {
            "curso": "Programación Orientada a Objetos",
            "nombre": "POO-A",
            "aforo": 35,
            "docente_idx": 4,
            "horarios": [
                {"dia_semana": 1, "hora_inicio": time(14, 0), "hora_final": time(16, 0), "aula": "Lab-206"},
                {"dia_semana": 3, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Lab-206"},
            ],
        },
        {
            "curso": "Ingeniería de Software I",
            "nombre": "IS1-A",
            "aforo": 30,
            "docente_idx": 4,
            "horarios": [
                {"dia_semana": 2, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Aula-201"},
                {"dia_semana": 4, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Aula-201"},
            ],
        },
        {
            "curso": "Ingeniería de Software II",
            "nombre": "IS2-A",
            "aforo": 28,
            "docente_idx": 1,
            "horarios": [
                {"dia_semana": 1, "hora_inicio": time(16, 0), "hora_final": time(18, 0), "aula": "Aula-202"},
                {"dia_semana": 3, "hora_inicio": time(16, 0), "hora_final": time(18, 0), "aula": "Aula-202"},
            ],
        },
        {
            "curso": "Redes de Computadoras",
            "nombre": "RED-A",
            "aforo": 30,
            "docente_idx": 5,
            "horarios": [
                {"dia_semana": 0, "hora_inicio": time(16, 0), "hora_final": time(18, 0), "aula": "Lab-Redes"},
                {"dia_semana": 2, "hora_inicio": time(16, 0), "hora_final": time(18, 0), "aula": "Lab-Redes"},
            ],
        },
        {
            "curso": "Inteligencia Artificial",
            "nombre": "IA-A",
            "aforo": 25,
            "docente_idx": 5,
            "horarios": [
                {"dia_semana": 1, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Lab-IA"},
                {"dia_semana": 4, "hora_inicio": time(14, 0), "hora_final": time(16, 0), "aula": "Lab-IA"},
            ],
        },
        {
            "curso": "Seguridad Informática",
            "nombre": "SEG-A",
            "aforo": 28,
            "docente_idx": 2,
            "horarios": [
                {"dia_semana": 2, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Aula-301"},
                {"dia_semana": 4, "hora_inicio": time(16, 0), "hora_final": time(18, 0), "aula": "Lab-Seg"},
            ],
        },
        {
            "curso": "Desarrollo de Aplicaciones Móviles",
            "nombre": "MOV-A",
            "aforo": 30,
            "docente_idx": 3,
            "horarios": [
                {"dia_semana": 0, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Lab-Movil"},
                {"dia_semana": 3, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Lab-Movil"},
            ],
        },
        {
            "curso": "Taller de Tesis I",
            "nombre": "TT1-A",
            "aforo": 20,
            "docente_idx": 0,
            "horarios": [
                {"dia_semana": 5, "hora_inicio": time(8, 0), "hora_final": time(12, 0), "aula": "Aula-Tesis"},
            ],
        },
        {
            "curso": "Calidad de Software",
            "nombre": "CS-A",
            "aforo": 30,
            "docente_idx": 4,
            "horarios": [
                {"dia_semana": 1, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Aula-210"},
                {"dia_semana": 3, "hora_inicio": time(14, 0), "hora_final": time(16, 0), "aula": "Lab-QA"},
            ],
        },
        {
            "curso": "Machine Learning",
            "nombre": "ML-A",
            "aforo": 25,
            "docente_idx": 5,
            "horarios": [
                {"dia_semana": 2, "hora_inicio": time(14, 0), "hora_final": time(16, 0), "aula": "Lab-IA"},
                {"dia_semana": 4, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Lab-IA"},
            ],
        },
        {
            "curso": "Sistemas Operativos",
            "nombre": "SO-A",
            "aforo": 35,
            "docente_idx": 3,
            "horarios": [
                {"dia_semana": 0, "hora_inicio": time(8, 0), "hora_final": time(10, 0), "aula": "Aula-115"},
                {"dia_semana": 2, "hora_inicio": time(10, 0), "hora_final": time(12, 0), "aula": "Lab-SO"},
            ],
        },
    ]

    for s in secciones_data:
        curso = cursos.get(s["curso"])
        docente = docentes[s["docente_idx"] % len(docentes)]
        if not curso:
            continue

        seccion = _safe_add(
            Seccion(
                curso_id=curso.id,
                docente_id=docente.id,
                periodo_academico_id=periodo_activo.id,
                nombre=s["nombre"],
                aforo=s["aforo"],
            ),
            f"Sección {s['nombre']}",
        )
        if seccion:
            for h in s["horarios"]:
                _safe_add(
                    Horario(seccion_id=seccion.id, **h),
                    f"Horario {s['nombre']} día {h['dia_semana']}",
                )

    # ── 8. Estudiantes (@sistema.edu) ───────────
    estudiantes_data = [
        {
            "nombres": "Estudiante",
            "apellidos": "Ejemplo",
            "email": "estudiante@sistema.edu",
            "dni": "33333333",
            "password": "estudiante123",
        },
        {
            "nombres": "José",
            "apellidos": "Araujo",
            "email": "jose.araujo@sistema.edu",
            "dni": "87654321",
            "password": "123456",
        },
        {
            "nombres": "María",
            "apellidos": "Torres",
            "email": "maria.torres@sistema.edu",
            "dni": "55667788",
            "password": "123456",
        },
        {
            "nombres": "Pedro",
            "apellidos": "Salazar",
            "email": "pedro.salazar@sistema.edu",
            "dni": "66778899",
            "password": "123456",
        },
        {
            "nombres": "Lucía",
            "apellidos": "Paredes",
            "email": "lucia.paredes@sistema.edu",
            "dni": "77889900",
            "password": "123456",
        },
        {
            "nombres": "Diego",
            "apellidos": "Castro",
            "email": "diego.castro@sistema.edu",
            "dni": "88990011",
            "password": "123456",
        },
    ]

    for data in estudiantes_data:
        user_est = User.query.filter_by(email=data["email"]).first()
        if not user_est:
            user_est = _safe_add(
                User(
                    nombres=data["nombres"],
                    apellidos=data["apellidos"],
                    email=data["email"],
                    password=generate_password_hash(data["password"]),
                    rol="estudiante",
                    dni=data["dni"],
                ),
                f"Usuario {data['email']}",
            )
        if user_est and plan:
            if not Estudiante.query.filter_by(user_id=user_est.id).first():
                _safe_add(
                    Estudiante(user_id=user_est.id, plan_estudios_id=plan.id),
                    f"Estudiante {data['email']}",
                )

    # ── 9. Tipos de documento ───────────────────
    tipos_documento_data = [
        {"nombre": "Constancia de estudios", "requiere_pago": False},
        {"nombre": "Certificado de notas", "requiere_pago": True},
        {"nombre": "Constancia de matrícula", "requiere_pago": True},
    ]
    tipos_creados = 0
    for t in tipos_documento_data:
        if not TipoDocumento.query.filter_by(nombre=t["nombre"]).first():
            _safe_add(
                TipoDocumento(nombre=t["nombre"], requiere_pago=t["requiere_pago"], activo=True),
                f"TipoDocumento {t['nombre']}",
            )
            tipos_creados += 1

    # ── Persistir ───────────────────────────────
    db.session.commit()
    print("[SEED] Datos de prueba insertados correctamente.")
    print(f"  Cursos: {len(cursos)}")
    print(f"  Periodos: {len(periodos)}")
    print(f"  Docentes: {len(docentes)}")
    print(f"  Tipos de documento nuevos: {tipos_creados}")
    print(f"  Secciones/horarios del periodo {periodo_activo.semestre} creados.")
    print("  Logins (@sistema.edu):")
    print("    admin@sistema.edu / admin123")
    print("    director@sistema.edu / director123")
    print("    docente@sistema.edu / docente123")
    print("    estudiante@sistema.edu / estudiante123")
