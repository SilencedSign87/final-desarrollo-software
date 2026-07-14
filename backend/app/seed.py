# -*- coding: utf-8 -*-
"""
Seeder extendido — datos de prueba "grandes" para QA de matrículas.

Crea, SIN tocar seed.py:
  - 2 facultades: Ingeniería de Sistemas e Ingeniería Civil
  - 1 plan de estudios por facultad, de 10 ciclos x 4 cursos c/u (40 cursos por plan)
  - Prerequisitos encadenados solo en 2 de las 4 posiciones de cada ciclo
    (las otras 2 posiciones de cada ciclo no tienen prerequisito)
  - 10 periodos académicos cerrados (histórico) + 1 activo + 1 planificado
  - 5 docentes por facultad
  - 20 estudiantes por facultad (40 en total), repartidos en los 10 ciclos
    (2 estudiantes por ciclo por facultad)
  - Para cada curso ya cursado: matrícula histórica validada, con 3
    evaluaciones (Parcial 50%, Prácticas 30%, Tareas 20%) y su promedio_final
    calculado exactamente igual que EvaluacionService, para que quede
    coherente con "aprobado" (>=10.5) / "desaprobado" (<10.5)
  - Se cuida que ningún ciclo completado tenga sus 4 cursos desaprobados
    (si no, el estudiante nunca habría podido avanzar de ciclo)
  - En el periodo activo, cada estudiante queda matriculado en los 4 cursos
    de su ciclo actual, y si tiene algún curso desaprobado previo, además
    se le matricula en un curso de reforzamiento (repitiendo el curso
    jalado), para poder probar el flujo de matrícula con cursos repetidos.
  - Cada Sección creada trae automáticamente sus 3 TipoEvaluacion por
    defecto (Parcial 50 / Practicas 30 / Tareas 20).

Uso:
    cd backend
    flask shell
    >>> from app.seed_extendido import run
    >>> run()

    o directo por consola:
    python -m app.seed_extendido
"""
import random
from datetime import datetime, time
from decimal import Decimal

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
from .models.horario import Horario
from .models.estudiante import Estudiante
from .models.matricula import Matricula
from .models.detalle_matricula import DetalleMatricula
from .models.tipo_evaluacion import TipoEvaluacion
from .models.evaluacion import Evaluacion

random.seed(42)  # reproducible: siempre genera el mismo dataset

NOTA_MINIMA_APROBATORIA = Decimal("10.5")

PESOS_EVALUACION = [
    ("Parcial", Decimal("50.00")),
    ("Practicas", Decimal("30.00")),
    ("Tareas", Decimal("20.00")),
]

# De las 4 posiciones de curso por ciclo (0,1,2,3), solo estas 2 forman una
# cadena de prerequisito con el mismo curso de la posición anterior.
# Las posiciones 2 y 3 de cada ciclo nunca tienen prerequisito.
POSICIONES_CON_PREREQ = (0, 1)

# ──────────────────────────────────────────────────────────────────────────
# Mallas curriculares: 10 ciclos x 4 cursos (nombre, horas_teoria, horas_practica)
# ──────────────────────────────────────────────────────────────────────────

MALLA_SISTEMAS = [
    [("Matemática Básica", 3, 2), ("Introducción a la Programación", 2, 4),
     ("Comunicación Oral y Escrita", 2, 2), ("Física I", 3, 2)],
    [("Matemática II", 3, 2), ("Programación Orientada a Objetos", 2, 4),
     ("Estructuras Discretas", 3, 2), ("Física II", 3, 2)],
    [("Matemática III", 3, 2), ("Estructura de Datos", 2, 4),
     ("Base de Datos I", 2, 3), ("Arquitectura de Computadoras", 3, 2)],
    [("Estadística", 3, 2), ("Algoritmos y Complejidad", 3, 2),
     ("Base de Datos II", 2, 3), ("Sistemas Operativos", 3, 2)],
    [("Investigación Operativa", 3, 2), ("Ingeniería de Software I", 3, 2),
     ("Redes de Computadoras", 2, 3), ("Análisis y Diseño de Sistemas", 2, 3)],
    [("Economía", 2, 1), ("Ingeniería de Software II", 2, 3),
     ("Desarrollo de Aplicaciones Móviles", 2, 4), ("Inteligencia Artificial", 3, 2)],
    [("Gestión de Proyectos de Software", 3, 2), ("Seguridad Informática", 2, 3),
     ("Computación en la Nube", 2, 3), ("Sistemas Distribuidos", 3, 2)],
    [("Arquitectura de Software", 3, 2), ("Machine Learning", 2, 3),
     ("Internet de las Cosas", 2, 3), ("Auditoría de Sistemas", 2, 2)],
    [("Desarrollo de Aplicaciones Web", 3, 4), ("Taller de Tesis I", 2, 2),
     ("Calidad de Software", 2, 3), ("Compiladores", 3, 2)],
    [("Ética Profesional", 2, 1), ("Taller de Tesis II", 2, 2),
     ("Prácticas Preprofesionales", 1, 4), ("Gestión de TI", 2, 2)],
]

MALLA_CIVIL = [
    [("Matemática Básica", 3, 2), ("Dibujo en Ingeniería", 1, 4),
     ("Comunicación Oral y Escrita", 2, 2), ("Química General", 3, 2)],
    [("Matemática II", 3, 2), ("Mecánica Vectorial", 3, 2),
     ("Física I", 3, 2), ("Geología General", 2, 2)],
    [("Matemática III", 3, 2), ("Resistencia de Materiales I", 3, 2),
     ("Física II", 3, 2), ("Topografía", 2, 3)],
    [("Ecuaciones Diferenciales", 3, 2), ("Resistencia de Materiales II", 3, 2),
     ("Mecánica de Fluidos", 3, 2), ("Estadística", 3, 2)],
    [("Métodos Numéricos", 2, 2), ("Análisis Estructural I", 3, 2),
     ("Mecánica de Suelos I", 2, 3), ("Materiales de Construcción", 2, 2)],
    [("Ingeniería Sísmica", 3, 2), ("Análisis Estructural II", 3, 2),
     ("Mecánica de Suelos II", 2, 3), ("Hidrología", 2, 2)],
    [("Concreto Armado I", 3, 2), ("Costos y Presupuestos", 2, 2),
     ("Ingeniería Sanitaria", 2, 2), ("Vías de Comunicación I", 2, 3)],
    [("Concreto Armado II", 3, 2), ("Ingeniería Antisísmica", 2, 2),
     ("Cimentaciones", 2, 3), ("Vías de Comunicación II", 2, 3)],
    [("Diseño de Puentes", 2, 2), ("Gestión de la Construcción", 2, 2),
     ("Impacto Ambiental", 2, 1), ("Taller de Tesis I", 2, 2)],
    [("Supervisión de Obras", 2, 2), ("Ética Profesional", 2, 1),
     ("Prácticas Preprofesionales", 1, 4), ("Taller de Tesis II", 2, 2)],
]

NOMBRES = [
    "José", "María", "Luis", "Ana", "Carlos", "Lucía", "Diego", "Patricia",
    "Roberto", "Fiorella", "Jorge", "Camila", "Miguel", "Valeria", "Andrés",
    "Gabriela", "Fernando", "Daniela", "Ricardo", "Karla", "Renato", "Milagros",
    "Sergio", "Ximena", "Álvaro", "Rosa", "Martín", "Carla", "Iván", "Sofía",
    "Julio", "Elena", "Bruno", "Paola", "Enrique", "Cinthia", "Raúl", "Diana",
    "Omar", "Yolanda",
]
APELLIDOS = [
    "Araujo", "Torres", "Salazar", "Paredes", "Castro", "Ramírez", "Mendoza",
    "Vargas", "Quispe", "Huamán", "Rojas", "Chávez", "Flores", "Gutiérrez",
    "Núñez", "Ibáñez", "Cárdenas", "Reyes", "Solís", "Delgado", "Cabrera",
    "Ponce", "Zúñiga", "Loayza", "Bravo", "Espinoza", "Guerrero", "Campos",
    "Herrera", "León",
]


def _safe_add(entity, desc="entidad"):
    try:
        with db.session.begin_nested():
            db.session.add(entity)
        return entity
    except Exception as e:
        print(f"  [SKIP] {desc}: {e}")
        return None


def _crear_facultad_completa(nombre_facultad, nombre_especialidad, malla, version_plan):
    facultad = _safe_add(Facultad(nombre=nombre_facultad), f"Facultad {nombre_facultad}")
    especialidad = _safe_add(
        Especialidad(facultad_id=facultad.id, nombre=nombre_especialidad, modalidad="presencial"),
        f"Especialidad {nombre_especialidad}",
    )
    plan = _safe_add(
        PlanEstudio(especialidad_id=especialidad.id, version=version_plan, anio=2024, estado="activo"),
        f"PlanEstudio {version_plan}",
    )
    db.session.flush()

    # cursos_por_ciclo[ciclo] = [Curso, Curso, Curso, Curso]
    cursos_por_ciclo = {}
    for idx_ciclo, cursos_del_ciclo in enumerate(malla, start=1):
        creados = []
        for nombre_curso, ht, hp in cursos_del_ciclo:
            curso = _safe_add(
                Curso(
                    plan_estudios_id=plan.id,
                    nombre=nombre_curso,
                    horas_teoria=ht,
                    horas_practica=hp,
                    semestre_num=idx_ciclo,
                ),
                f"Curso {nombre_curso}",
            )
            creados.append(curso)
        cursos_por_ciclo[idx_ciclo] = creados
    db.session.flush()

    # Prerequisitos: solo posiciones 0 y 1 de cada ciclo, encadenadas con el
    # ciclo inmediato anterior en la misma posición.
    for idx_ciclo in range(2, 11):
        actuales = cursos_por_ciclo[idx_ciclo]
        anteriores = cursos_por_ciclo[idx_ciclo - 1]
        for pos in POSICIONES_CON_PREREQ:
            if actuales[pos] and anteriores[pos]:
                actuales[pos].prerequisitos.append(anteriores[pos])

    db.session.flush()
    return facultad, especialidad, plan, cursos_por_ciclo


def _crear_periodos():
    periodos = {}
    anios = [2021, 2022, 2023, 2024, 2025]
    orden = []
    for anio in anios:
        for sem in ("I", "II"):
            orden.append(f"{anio}-{sem}")

    for i, semestre in enumerate(orden):  # 10 periodos cerrados (histórico)
        anio = int(semestre.split("-")[0])
        mes_inicio = 3 if semestre.endswith("I") and not semestre.endswith("II") else 8
        p = _safe_add(
            PeriodoAcademico(
                semestre=semestre,
                fecha_inicio=datetime(anio, mes_inicio, 1),
                fecha_fin=datetime(anio, mes_inicio + 4, 28),
                estado="cerrado",
                requiere_pago=True,
            ),
            f"Periodo {semestre}",
        )
        periodos[semestre] = p

    activo = _safe_add(
        PeriodoAcademico(
            semestre="2026-I",
            fecha_inicio=datetime(2026, 3, 1),
            fecha_fin=datetime(2026, 7, 15),
            estado="activo",
            requiere_pago=True,
        ),
        "Periodo 2026-I",
    )
    periodos["2026-I"] = activo

    planificado = _safe_add(
        PeriodoAcademico(
            semestre="2026-II",
            fecha_inicio=datetime(2026, 8, 17),
            fecha_fin=datetime(2026, 12, 18),
            estado="planificado",
            requiere_pago=False,
        ),
        "Periodo 2026-II",
    )
    periodos["2026-II"] = planificado

    db.session.flush()
    # Lista ordenada de los 10 periodos cerrados, ciclo 1 -> orden[0], etc.
    periodos_cerrados_ordenados = [periodos[s] for s in orden]
    return periodos, periodos_cerrados_ordenados, activo


def _crear_docentes(prefijo_dni, cantidad, dominio_email):
    docentes = []
    categorias = ["principal", "asociado", "auxiliar"]
    for i in range(cantidad):
        nombres = random.choice(NOMBRES)
        apellidos = random.choice(APELLIDOS)
        email = f"docente.{prefijo_dni}{i}@{dominio_email}"
        dni = f"{prefijo_dni}{i:04d}"
        user = _safe_add(
            User(
                nombres=nombres,
                apellidos=apellidos,
                email=email,
                password=generate_password_hash("docente123"),
                rol="docente",
                dni=dni,
            ),
            f"Usuario docente {email}",
        )
        db.session.flush()
        docente = _safe_add(
            Docente(user_id=user.id, categoria=random.choice(categorias)),
            f"Docente {email}",
        )
        docentes.append(docente)
    db.session.flush()
    return docentes


class SeccionFactory:
    """Crea (o reutiliza) una Sección por cada par (curso, periodo), y le
    agrega automáticamente sus 3 tipos de evaluación por defecto."""

    def __init__(self, docentes):
        self.docentes = docentes
        self._cache = {}
        self._contador_horario = 0

    def obtener(self, curso, periodo):
        key = (curso.id, periodo.id)
        if key in self._cache:
            return self._cache[key]

        docente = self.docentes[curso.id % len(self.docentes)]
        nombre_seccion = f"{curso.nombre[:3].upper()}-{periodo.semestre}"
        seccion = _safe_add(
            Seccion(
                curso_id=curso.id,
                docente_id=docente.id,
                periodo_academico_id=periodo.id,
                nombre=nombre_seccion,
                aforo=35,
            ),
            f"Sección {nombre_seccion}",
        )
        db.session.flush()

        dia = self._contador_horario % 6
        self._contador_horario += 1
        _safe_add(
            Horario(
                seccion_id=seccion.id,
                dia_semana=dia,
                hora_inicio=time(8, 0),
                hora_final=time(10, 0),
                aula=f"Aula-{100 + (curso.id % 20)}",
            ),
            f"Horario {nombre_seccion}",
        )

        for nombre_tipo, peso in PESOS_EVALUACION:
            _safe_add(
                TipoEvaluacion(seccion_id=seccion.id, nombre=nombre_tipo, peso=peso),
                f"TipoEvaluacion {nombre_tipo} de {nombre_seccion}",
            )
        db.session.flush()

        self._cache[key] = seccion
        return seccion


def _generar_notas(aprobado):
    """Devuelve 3 notas (Decimal) para Parcial/Practicas/Tareas que, al
    ponderar 50/30/20, garantizan que el promedio caiga en el rango deseado.
    """
    if aprobado:
        valores = [random.randint(11, 19) for _ in range(3)]
    else:
        valores = [random.randint(4, 9) for _ in range(3)]
    return [Decimal(v) for v in valores]


def _registrar_curso(estudiante, seccion, matricula, aprobado, finalizado):
    detalle = _safe_add(
        DetalleMatricula(
            matricula_id=matricula.id,
            seccion_id=seccion.id,
            estado_curso="matriculado",
            is_validated=False,
        ),
        f"DetalleMatricula est={estudiante.id} seccion={seccion.id}",
    )
    db.session.flush()

    if not finalizado:
        return detalle  # curso en curso (periodo activo): sin notas todavía

    tipos = TipoEvaluacion.query.filter_by(seccion_id=seccion.id).order_by(TipoEvaluacion.id).all()
    notas = _generar_notas(aprobado)

    suma_ponderada = Decimal("0")
    suma_pesos = Decimal("0")
    for tipo, nota in zip(tipos, notas):
        _safe_add(
            Evaluacion(tipo_evaluacion_id=tipo.id, detalle_matricula_id=detalle.id, nota=nota),
            f"Evaluacion {tipo.nombre} est={estudiante.id}",
        )
        suma_ponderada += nota * tipo.peso
        suma_pesos += tipo.peso

    promedio = (suma_ponderada / suma_pesos).quantize(Decimal("0.00"))
    detalle.promedio_final = promedio
    detalle.is_validated = True
    detalle.estado_curso = "aprobado" if promedio >= NOTA_MINIMA_APROBATORIA else "desaprobado"
    return detalle


def _crear_estudiante_con_historial(
    plan, cursos_por_ciclo, periodos_cerrados_ordenados, periodo_activo,
    seccion_factory, ciclo_actual, prefijo_dni, indice, dominio_email,
    sin_matricular=False,
):
    nombres = random.choice(NOMBRES)
    apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
    email = f"estudiante.{prefijo_dni}{indice}@{dominio_email}"
    dni = f"{prefijo_dni}{indice:04d}"

    user = _safe_add(
        User(
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            password=generate_password_hash("estudiante123"),
            rol="estudiante",
            dni=dni,
        ),
        f"Usuario estudiante {email}",
    )
    db.session.flush()
    estudiante = _safe_add(
        Estudiante(user_id=user.id, plan_estudios_id=plan.id),
        f"Estudiante {email}",
    )
    db.session.flush()

    cursos_desaprobados = []  # (curso, seccion) para posible reforzamiento

    # ── Ciclos ya completados (1 .. ciclo_actual - 1) ──
    for ciclo in range(1, ciclo_actual):
        periodo = periodos_cerrados_ordenados[ciclo - 1]
        cursos_ciclo = cursos_por_ciclo[ciclo]

        matricula = _safe_add(
            Matricula(
                periodo_academico_id=periodo.id,
                estudiante_id=estudiante.id,
                estado="validada",
                comprobante_url=None,
            ),
            f"Matricula hist. est={estudiante.id} periodo={periodo.semestre}",
        )
        db.session.flush()

        # Nunca desaprobar los 4 cursos del mismo ciclo (si no, el
        # estudiante nunca habría podido avanzar al siguiente ciclo).
        # Además, solo se hacen fallar cursos en posiciones SIN cadena de
        # prerequisito (2 y 3), para que nunca quede un curso "aprobado"
        # cuyo prerequisito haya sido desaprobado.
        posiciones_falleables = [p for p in range(4) if p not in POSICIONES_CON_PREREQ]
        n_fallos = random.choice([0, 0, 1, 1, len(posiciones_falleables)])
        posiciones_fallo = (
            set(random.sample(posiciones_falleables, n_fallos)) if n_fallos else set()
        )

        for pos, curso in enumerate(cursos_ciclo):
            seccion = seccion_factory.obtener(curso, periodo)
            aprobado = pos not in posiciones_fallo
            detalle = _registrar_curso(estudiante, seccion, matricula, aprobado, finalizado=True)
            if not aprobado:
                cursos_desaprobados.append((curso, seccion))

    # ── Ciclo actual: matrícula en el periodo activo ──
    # (si sin_matricular=True, el estudiante se queda SIN matrícula en el
    # periodo activo a propósito, para poder probar el flujo de
    # "Matricularme" desde cero en la UI)
    if not sin_matricular:
        cursos_ciclo_actual = cursos_por_ciclo[ciclo_actual]
        estado_matricula = "validada" if random.random() < 0.75 else "pendiente"
        matricula_activa = _safe_add(
            Matricula(
                periodo_academico_id=periodo_activo.id,
                estudiante_id=estudiante.id,
                estado=estado_matricula,
                comprobante_url=None,
            ),
            f"Matricula activa est={estudiante.id}",
        )
        db.session.flush()

        for curso in cursos_ciclo_actual:
            seccion = seccion_factory.obtener(curso, periodo_activo)
            _registrar_curso(estudiante, seccion, matricula_activa, aprobado=None, finalizado=False)

        # Si tiene algún curso jalado, lo matricula también en un curso de
        # reforzamiento (repitiendo un curso desaprobado) dentro del mismo
        # periodo activo -> para poder probar matrícula con cursos repetidos.
        if cursos_desaprobados:
            curso_repetir, _ = random.choice(cursos_desaprobados)
            seccion_repite = seccion_factory.obtener(curso_repetir, periodo_activo)
            _registrar_curso(estudiante, seccion_repite, matricula_activa, aprobado=None, finalizado=False)

    return estudiante


def _crear_usuarios_gestion():
    """Crea un usuario 'administrador' y uno de 'direccion' (rol que en este
    sistema cumple el papel de personal administrativo: valida matrículas,
    documentos, ve reportes, etc. — ver /api/roles, los únicos 4 roles que
    existen son estudiante, docente, administrador y direccion).

    Se usan emails distintos a los de seed.py (admin@sistema.edu /
    director@sistema.edu) para poder correr ambos seeders sin choques.
    """
    usuarios = [
        {
            "nombres": "Administrador",
            "apellidos": "General",
            "rol": "administrador",
            "dni": "90000001",
            "email": "admin.general@sistema.edu",
            "password": "admin123",
        },
        {
            "nombres": "Personal",
            "apellidos": "Administrativo",
            "rol": "direccion",
            "dni": "90000002",
            "email": "administrativo@sistema.edu",
            "password": "administrativo123",
        },
    ]
    for u in usuarios:
        if User.query.filter_by(email=u["email"]).first():
            continue
        _safe_add(
            User(
                nombres=u["nombres"],
                apellidos=u["apellidos"],
                rol=u["rol"],
                dni=u["dni"],
                email=u["email"],
                password=generate_password_hash(u["password"]),
            ),
            f"Usuario {u['email']}",
        )
    db.session.flush()


def run():
    if Facultad.query.filter(
        Facultad.nombre.in_(["Ingeniería de Sistemas", "Ingeniería Civil"])
    ).first():
        print("[SEED-EXT] Ya existen facultades 'Ingeniería de Sistemas' / 'Ingeniería Civil'. "
              "No se vuelve a ejecutar (evita duplicados). Si quieres regenerar, borra esos "
              "registros primero.")
        return

    print("[SEED-EXT] Creando facultades, especialidades y planes...")
    fac_sis, _, plan_sis, cursos_sis = _crear_facultad_completa(
        "Ingeniería de Sistemas", "Ingeniería de Sistemas", MALLA_SISTEMAS, "2024-SIS"
    )
    fac_civ, _, plan_civ, cursos_civ = _crear_facultad_completa(
        "Ingeniería Civil", "Ingeniería Civil", MALLA_CIVIL, "2024-CIV"
    )

    print("[SEED-EXT] Creando periodos académicos...")
    periodos, periodos_cerrados_ordenados, periodo_activo = _crear_periodos()

    print("[SEED-EXT] Creando docentes...")
    docentes_sis = _crear_docentes("5000", 5, "sistemas.edu")
    docentes_civ = _crear_docentes("6000", 5, "civil.edu")

    factory_sis = SeccionFactory(docentes_sis)
    factory_civ = SeccionFactory(docentes_civ)

    # Ciclo 1 (i=0..1) se deja siempre matriculado (recién ingresante, no
    # tendría sentido que no se matricule). El resto de índices %5==3 queda
    # SIN matrícula en el periodo activo, para probar el flujo desde la UI.
    print("[SEED-EXT] Creando 20 estudiantes de Sistemas (repartidos en 10 ciclos)...")
    for i in range(20):
        ciclo = (i % 10) + 1
        sin_matricular = i % 5 == 3
        _crear_estudiante_con_historial(
            plan_sis, cursos_sis, periodos_cerrados_ordenados, periodo_activo,
            factory_sis, ciclo, "7000", i, "sistemas.edu",
            sin_matricular=sin_matricular,
        )

    print("[SEED-EXT] Creando 20 estudiantes de Civil (repartidos en 10 ciclos)...")
    for i in range(20):
        ciclo = (i % 10) + 1
        sin_matricular = i % 5 == 3
        _crear_estudiante_con_historial(
            plan_civ, cursos_civ, periodos_cerrados_ordenados, periodo_activo,
            factory_civ, ciclo, "8000", i, "civil.edu",
            sin_matricular=sin_matricular,
        )

    print("[SEED-EXT] Creando usuarios administrador y direccion (administrativo)...")
    _crear_usuarios_gestion()

    db.session.commit()
    print("[SEED-EXT] Listo.")
    print("  Facultades: Ingeniería de Sistemas, Ingeniería Civil")
    print("  Cursos por plan: 40 (10 ciclos x 4)")
    print("  Periodos: 10 cerrados (2021-I .. 2025-II) + 2026-I activo + 2026-II planificado")
    print("  Docentes: 5 (Sistemas, dominio sistemas.edu) + 5 (Civil, dominio civil.edu)")
    print("  Estudiantes SIN matrícula en 2026-I (para probar 'Matricularme'): "
          "estudiante.70003, estudiante.70008, estudiante.70013, estudiante.70018 (Sistemas) / "
          "estudiante.80003, estudiante.80008, estudiante.80013, estudiante.80018 (Civil)")
    print("  Estudiantes: 20 Sistemas + 20 Civil, repartidos ciclo 1..10 (2 por ciclo c/u)")
    print("  Login estudiantes: estudiante.7000{0..19}@sistemas.edu / estudiante123")
    print("                     estudiante.8000{0..19}@civil.edu / estudiante123")
    print("  Login docentes:    docente.5000{0..4}@sistemas.edu / docente123")
    print("                     docente.6000{0..4}@civil.edu / docente123")
    print("  Login administrador:  admin.general@sistema.edu / admin123")
    print("  Login direccion (administrativo): administrativo@sistema.edu / administrativo123")


if __name__ == "__main__":
    from . import create_app

    app = create_app()
    with app.app_context():
        run()
