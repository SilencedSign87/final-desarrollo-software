"""
Script de datos de prueba (seed) para probar el módulo de Matrícula.

Cómo correrlo (parado en la carpeta backend/, con el venv activado):
    python seed_test_data.py

Crea la cadena completa de dependencias necesarias:
Facultad -> Especialidad -> PlanEstudio -> Curso -> PeriodoAcademico
-> Docente (+ User) -> Seccion -> Estudiante (+ User)

Es seguro correrlo varias veces sobre una BD ya poblada por este script
(usa get_or_create simple por nombre para no duplicar).
"""
from datetime import datetime, time
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.facultad import Facultad
from app.models.especialidad import Especialidad
from app.models.plan_estudio import PlanEstudio
from app.models.curso import Curso
from app.models.periodo_academico import PeriodoAcademico
from app.models.docente import Docente
from app.models.seccion import Seccion
from app.models.estudiante import Estudiante
from app.models.horario import Horario

app = create_app()

with app.app_context():
    facultad = Facultad.query.filter_by(nombre="Ingeniería de Sistemas").first()
    if not facultad:
        facultad = Facultad(nombre="Ingeniería de Sistemas")
        db.session.add(facultad)
        db.session.flush()

    especialidad = Especialidad.query.filter_by(nombre="Sistemas").first()
    if not especialidad:
        especialidad = Especialidad(
            facultad_id=facultad.id, nombre="Sistemas", modalidad="presencial"
        )
        db.session.add(especialidad)
        db.session.flush()

    plan = PlanEstudio.query.filter_by(especialidad_id=especialidad.id).first()
    if not plan:
        plan = PlanEstudio(
            especialidad_id=especialidad.id, version="2024", anio=2024, estado="activo"
        )
        db.session.add(plan)
        db.session.flush()

    curso = Curso.query.filter_by(nombre="Desarrollo de Aplicaciones Web").first()
    if not curso:
        curso = Curso(
            plan_estudios_id=plan.id,
            nombre="Desarrollo de Aplicaciones Web",
            horas_teoria=3,
            horas_practica=4,
            semestre_num=9,
        )
        db.session.add(curso)
        db.session.flush()

    periodo = PeriodoAcademico.query.filter_by(semestre="2026-I").first()
    if not periodo:
        periodo = PeriodoAcademico(
            semestre="2026-I",
            fecha_inicio=datetime(2026, 3, 1),
            fecha_fin=datetime(2026, 7, 15),
            estado="activo",
        )
        db.session.add(periodo)
        db.session.flush()

    # Usuario docente + perfil Docente
    user_docente = User.query.filter_by(email="docente.prueba@uncp.edu.pe").first()
    if not user_docente:
        user_docente = User(
            nombres="Carlos",
            apellidos="Ramírez",
            email="docente.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="docente",
            dni="12345678",
        )
        db.session.add(user_docente)
        db.session.flush()

    docente = Docente.query.filter_by(user_id=user_docente.id).first()
    if not docente:
        docente = Docente(user_id=user_docente.id, categoria="asociado")
        db.session.add(docente)
        db.session.flush()

    seccion = Seccion.query.filter_by(nombre="DAW-A").first()
    if not seccion:
        seccion = Seccion(
            curso_id=curso.id,
            docente_id=docente.id,
            periodo_academico_id=periodo.id,
            nombre="DAW-A",
            aforo=30,
        )
        db.session.add(seccion)
        db.session.flush()

    horario = Horario.query.filter_by(seccion_id=seccion.id).first()
    if not horario:
        horario = Horario(
            seccion_id=seccion.id,
            dia_semana=0,  # lunes
            hora_inicio=time(8, 0),
            hora_final=time(10, 0),
            aula="Lab-201",
        )
        db.session.add(horario)
        db.session.flush()

    # Usuario estudiante + perfil Estudiante
    user_estudiante = User.query.filter_by(email="estudiante.prueba@uncp.edu.pe").first()
    if not user_estudiante:
        user_estudiante = User(
            nombres="José",
            apellidos="Araujo",
            email="estudiante.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="estudiante",
            dni="87654321",
        )
        db.session.add(user_estudiante)
        db.session.flush()

    estudiante = Estudiante.query.filter_by(user_id=user_estudiante.id).first()
    if not estudiante:
        estudiante = Estudiante(user_id=user_estudiante.id, plan_estudios_id=plan.id)
        db.session.add(estudiante)
        db.session.flush()

    # Segundo usuario estudiante (para probar que NO pueda ver matrículas ajenas)
    user_estudiante_2 = User.query.filter_by(email="estudiante2.prueba@uncp.edu.pe").first()
    if not user_estudiante_2:
        user_estudiante_2 = User(
            nombres="María",
            apellidos="Torres",
            email="estudiante2.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="estudiante",
            dni="55667788",
        )
        db.session.add(user_estudiante_2)
        db.session.flush()

    estudiante_2 = Estudiante.query.filter_by(user_id=user_estudiante_2.id).first()
    if not estudiante_2:
        estudiante_2 = Estudiante(user_id=user_estudiante_2.id, plan_estudios_id=plan.id)
        db.session.add(estudiante_2)
        db.session.flush()

    # Usuario administrador (para probar /validar)
    user_admin = User.query.filter_by(email="admin.prueba@uncp.edu.pe").first()
    if not user_admin:
        user_admin = User(
            nombres="Admin",
            apellidos="Prueba",
            email="admin.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="administrador",
            dni="11223344",
        )
        db.session.add(user_admin)

    # Usuario dirección (para probar /carga-docente y /estadisticas)
    user_direccion = User.query.filter_by(email="direccion.prueba@uncp.edu.pe").first()
    if not user_direccion:
        user_direccion = User(
            nombres="Directora",
            apellidos="Prueba",
            email="direccion.prueba@uncp.edu.pe",
            password=generate_password_hash("123456"),
            rol="direccion",
            dni="99887766",
        )
        db.session.add(user_direccion)

    db.session.commit()

    print("Datos de prueba creados correctamente:")
    print(f"  Curso de prueba -> id={curso.id} ('{curso.nombre}')")
    print(f"  Periodo académico -> id={periodo.id} ('{periodo.semestre}')")
    print(f"  Docente -> id={docente.id}")
    print(f"  Sección de prueba -> id={seccion.id} ('{seccion.nombre}')")
    print(f"  Horario de prueba -> id={horario.id} (lunes 08:00-10:00, Lab-201)")
    print("  Estudiante -> estudiante.prueba@uncp.edu.pe / 123456")
    print("  Estudiante 2 (para probar seguridad) -> estudiante2.prueba@uncp.edu.pe / 123456")
    print("  Administrador -> admin.prueba@uncp.edu.pe / 123456")
    print("  Docente (login) -> docente.prueba@uncp.edu.pe / 123456")
    print("  Dirección -> direccion.prueba@uncp.edu.pe / 123456")