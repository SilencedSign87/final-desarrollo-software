from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from ..extensions import db
from ..models.matricula import Matricula
from ..models.detalle_matricula import DetalleMatricula
from ..models.seccion import Seccion
from ..models.estudiante import Estudiante
from ..models.periodo_academico import PeriodoAcademico
from ..services.curso_service import CursoService
from .file_service import FileService


class MatriculaService:

    @staticmethod
    def crear_matricula(estudiante_id, data, comprobante_file=None):
        """
        Crea una matrícula en estado 'pendiente' junto con sus detalles.
        Valida cupos, prerequisitos, semestre y, si el periodo lo exige,
        el comprobante de pago (archivo o URL).
        """
        periodo = PeriodoAcademico.query.get(data["periodo_academico_id"])
        if not periodo:
            raise ValueError("El periodo académico no existe")

        secciones_ids = list(dict.fromkeys(data["secciones_ids"]))

        secciones = Seccion.query.filter(
            Seccion.id.in_(secciones_ids)
        ).all()

        if len(secciones) != len(secciones_ids):
            raise ValueError("Una o más secciones no existen")

        matricula_existente = Matricula.query.filter(
            Matricula.estudiante_id == estudiante_id,
            Matricula.periodo_academico_id == periodo.id,
            Matricula.estado.in_(["pendiente", "validada"]),
        ).first()
        if matricula_existente:
            raise ValueError(
                f"Ya existe una matrícula {matricula_existente.estado} para este "
                f"periodo (id={matricula_existente.id}). No se puede crear otra."
            )

        for seccion in secciones:
            if seccion.periodo_academico_id != periodo.id:
                raise ValueError(
                    f"La sección '{seccion.nombre}' no pertenece al periodo académico indicado"
                )

        cursos_vistos = {}
        for seccion in secciones:
            if seccion.curso_id in cursos_vistos:
                raise ValueError(
                    f"Seleccionaste dos secciones del mismo curso "
                    f"'{seccion.curso.nombre}' ({cursos_vistos[seccion.curso_id]} y {seccion.nombre})"
                )
            cursos_vistos[seccion.curso_id] = seccion.nombre

        semestre_actual, aprobados_ids = (
            CursoService.obtener_semestre_actual_y_aprobados(estudiante_id)
        )
        for seccion in secciones:
            curso = seccion.curso
            if curso.semestre_num > semestre_actual:
                raise ValueError(
                    f"El curso '{curso.nombre}' pertenece al semestre "
                    f"{curso.semestre_num}, pero el estudiante está en el "
                    f"semestre {semestre_actual}"
                )
            if curso.id in aprobados_ids:
                raise ValueError(
                    f"El curso '{curso.nombre}' ya fue aprobado, no se puede "
                    f"volver a matricular"
                )
            prereqs_faltantes = [
                p.nombre for p in curso.prerequisitos if p.id not in aprobados_ids
            ]
            if prereqs_faltantes:
                raise ValueError(
                    f"No cumple los prerequisitos de '{curso.nombre}': "
                    f"falta aprobar {', '.join(prereqs_faltantes)}"
                )

        for seccion in secciones:
            ya_matriculados = DetalleMatricula.query.filter_by(
                seccion_id=seccion.id
            ).count()
            if ya_matriculados >= seccion.aforo:
                raise ValueError(
                    f"La sección '{seccion.nombre}' ya no tiene cupos disponibles"
                )

        comprobante_url = data.get("comprobante_url")
        tiene_archivo = comprobante_file is not None and getattr(
            comprobante_file, "filename", None
        )

        if periodo.requiere_pago and not tiene_archivo and not comprobante_url:
            raise ValueError(
                "Este periodo requiere comprobante de pago. Adjunta el archivo."
            )

        if tiene_archivo:
            FileService.validate_comprobante(comprobante_file)

        matricula = Matricula(
            periodo_academico_id=periodo.id,
            estudiante_id=estudiante_id,
            estado="pendiente",
            comprobante_url=comprobante_url,
        )
        db.session.add(matricula)
        db.session.flush()

        for seccion in secciones:
            detalle = DetalleMatricula(
                matricula_id=matricula.id,
                seccion_id=seccion.id,
                estado_curso="matriculado",
            )
            db.session.add(detalle)

        if tiene_archivo:
            stored = FileService.save_comprobante(
                comprobante_file, f"matricula-{matricula.id}"
            )
            matricula.comprobante_url = stored

        db.session.commit()
        return matricula

    @staticmethod
    def listar_matriculas(estado=None):
        query = Matricula.query
        if estado:
            query = query.filter_by(estado=estado)
        return query.all()

    @staticmethod
    def listar_matriculas_por_estudiante(estudiante_id):
        """Lista únicamente las matrículas del estudiante indicado (para su propia vista)"""
        return Matricula.query.filter_by(estudiante_id=estudiante_id).all()

    @staticmethod
    def obtener_matricula(matricula_id):
        return Matricula.query.get(matricula_id)

    @staticmethod
    def validar_matricula(matricula_id, admin_user_id, data):
        matricula = Matricula.query.get(matricula_id)
        if not matricula:
            return None

        matricula.estado = data["estado"]
        matricula.observacion = data.get("observacion")
        matricula.validado_user_id = admin_user_id

        db.session.commit()
        return matricula

    @staticmethod
    def obtener_estudiante_por_user_id(user_id):
        return Estudiante.query.filter_by(user_id=user_id).first()

    @staticmethod
    def estadisticas():
        """Conteo de matrículas agrupado por estado"""
        resultados = (
            db.session.query(Matricula.estado, db.func.count(Matricula.id))
            .group_by(Matricula.estado)
            .all()
        )
        return {estado: total for estado, total in resultados}

    @staticmethod
    def generar_ficha_pdf(matricula_id):
        """
        Genera el PDF de la ficha de matrícula con los datos del estudiante,
        periodo académico, cursos matriculados y quién la validó.
        Lanza ValueError si la matrícula no está en estado 'validada'
        (no tiene sentido entregar una ficha oficial de algo aún no aprobado).
        Devuelve un BytesIO con el PDF listo para enviar, o None si no existe.
        """
        matricula = Matricula.query.get(matricula_id)
        if not matricula:
            return None

        if matricula.estado != "validada":
            raise ValueError(
                "Solo se puede descargar la ficha de una matrícula validada"
            )

        estudiante = matricula.estudiante
        user = estudiante.user
        periodo = matricula.periodo_academico

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        y = height - 2 * cm
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, "FICHA DE MATRÍCULA")
        y -= 0.8 * cm
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y, "Universidad Nacional del Centro del Perú")
        y -= 1.5 * cm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, "Datos del estudiante")
        y -= 0.7 * cm
        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, f"Nombre: {user.nombres} {user.apellidos}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"DNI: {user.dni}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Periodo académico: {periodo.semestre}")
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Estado de matrícula: {matricula.estado.upper()}")
        y -= 1 * cm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, "Cursos matriculados")
        y -= 0.8 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2 * cm, y, "Curso")
        c.drawString(10 * cm, y, "Sección")
        c.drawString(14 * cm, y, "Estado")
        y -= 0.3 * cm
        c.line(2 * cm, y, width - 2 * cm, y)
        y -= 0.5 * cm

        c.setFont("Helvetica", 9)
        for detalle in matricula.detalles:
            seccion = detalle.seccion
            c.drawString(2 * cm, y, seccion.curso.nombre[:45])
            c.drawString(10 * cm, y, seccion.nombre)
            c.drawString(14 * cm, y, detalle.estado_curso)
            y -= 0.5 * cm

        y -= 1 * cm
        if matricula.validador:
            c.setFont("Helvetica", 9)
            c.drawString(
                2 * cm,
                y,
                f"Validado por: {matricula.validador.nombres} {matricula.validador.apellidos}",
            )

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
