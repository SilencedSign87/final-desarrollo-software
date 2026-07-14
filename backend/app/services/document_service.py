import io
import secrets
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import qrcode
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..extensions import db
from ..models.curso import Curso
from ..models.detalle_matricula import DetalleMatricula
from ..models.matricula import Matricula
from ..models.seccion import Seccion
from ..models.solicitud_documento import SolicitudDocumento
from ..services.curso_service import CursoService
from ..services.evaluacion_service import EvaluacionService
from ..utils.url_utils import public_api_url
from .signature_service import SignatureService


class DocumentService:
    INSTITUTION_NAME = "Universidad Nacional del Centro del Perú"

    # Tipos del catálogo por defecto (seed) con plantilla específica
    STANDARD_DOCUMENT_TYPES = {
        "constancia de estudios": "constancia_estudios",
        "certificado de notas": "certificado_notas",
        "constancia de matricula": "constancia_matricula",
    }

    @staticmethod
    def _documents_dir() -> Path:
        folder = Path(current_app.config["DOCUMENTS_FOLDER"])
        if not folder.is_absolute():
            folder = Path(current_app.root_path).parent / folder
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def build_verification_url(qr_hash: str) -> str:
        return public_api_url(f"/api/documentos/verificar/{qr_hash}")

    @staticmethod
    def build_download_url(solicitud_id: int) -> str:
        return public_api_url(f"/api/documentos/solicitudes/{solicitud_id}/archivo")

    @staticmethod
    def generate_qr_hash() -> str:
        return secrets.token_hex(16)

    @staticmethod
    def generate_ticket_code(fecha: datetime | None = None) -> str:
        moment = fecha or datetime.now(timezone.utc)
        year = moment.year
        prefix = f"REQ-{year}-"
        last = (
            SolicitudDocumento.query.filter(
                SolicitudDocumento.codigo_ticket.like(f"{prefix}%")
            )
            .order_by(SolicitudDocumento.codigo_ticket.desc())
            .first()
        )
        if last and last.codigo_ticket:
            try:
                correlativo = int(last.codigo_ticket.rsplit("-", 1)[-1]) + 1
            except ValueError:
                correlativo = 1
        else:
            correlativo = 1
        return f"{prefix}{correlativo:04d}"

    @staticmethod
    def _build_qr_image(verification_url: str) -> io.BytesIO:
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(verification_url)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @staticmethod
    def _student_name(solicitud) -> str:
        user = solicitud.estudiante.user
        return f"{user.nombres} {user.apellidos}"

    @staticmethod
    def _student_dni(solicitud) -> str:
        return solicitud.estudiante.user.dni

    @staticmethod
    def _normalize_tipo(tipo: str) -> str:
        text = (tipo or "").lower().strip()
        text = unicodedata.normalize("NFD", text)
        return "".join(char for char in text if unicodedata.category(char) != "Mn")

    @classmethod
    def _resolve_template_key(cls, tipo: str) -> str | None:
        """Solo los 3 tipos por defecto tienen plantilla específica."""
        return cls.STANDARD_DOCUMENT_TYPES.get(cls._normalize_tipo(tipo))

    @classmethod
    def _academic_profile(cls, solicitud) -> dict:
        plan = solicitud.estudiante.plan_estudio
        especialidad = plan.especialidad if plan else None
        facultad = especialidad.facultad if especialidad else None
        semestre_actual, _ = CursoService.obtener_semestre_actual_y_aprobados(
            solicitud.estudiante_id
        )

        return {
            "facultad": facultad.nombre if facultad else "No registrada",
            "especialidad": especialidad.nombre if especialidad else "No registrada",
            "modalidad": especialidad.modalidad if especialidad else "No registrada",
            "plan_version": plan.version if plan else "No registrado",
            "plan_anio": plan.anio if plan else "—",
            "semestre_actual": semestre_actual,
        }

    @staticmethod
    def _latest_matricula(estudiante_id: int):
        matricula = (
            Matricula.query.filter_by(estudiante_id=estudiante_id, estado="validada")
            .order_by(Matricula.id.desc())
            .first()
        )
        if matricula:
            return matricula
        return (
            Matricula.query.filter_by(estudiante_id=estudiante_id)
            .order_by(Matricula.id.desc())
            .first()
        )

    @staticmethod
    def _matricula_courses(matricula):
        if not matricula:
            return []
        return (
            db.session.query(DetalleMatricula, Seccion, Curso)
            .join(Seccion, Seccion.id == DetalleMatricula.seccion_id)
            .join(Curso, Curso.id == Seccion.curso_id)
            .filter(DetalleMatricula.matricula_id == matricula.id)
            .order_by(Curso.nombre.asc())
            .all()
        )

    @staticmethod
    def _table_style():
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )

    @classmethod
    def _build_common_header(cls, solicitud, title_style, subtitle_style, body_style):
        profile = cls._academic_profile(solicitud)
        ticket = solicitud.codigo_ticket or f"#{solicitud.id}"
        issued_at = datetime.now(timezone.utc).strftime("%d/%m/%Y")

        return [
            Paragraph(cls.INSTITUTION_NAME, title_style),
            Paragraph(solicitud.tipo_documento.upper(), title_style),
            Paragraph("Documento oficial emitido por el sistema académico", subtitle_style),
            Spacer(1, 0.15 * inch),
            Paragraph(f"<b>Código de ticket:</b> {ticket}", body_style),
            Paragraph(f"<b>Fecha de emisión:</b> {issued_at}", body_style),
            Paragraph(f"<b>Estudiante:</b> {cls._student_name(solicitud)}", body_style),
            Paragraph(f"<b>DNI:</b> {cls._student_dni(solicitud)}", body_style),
            Paragraph(f"<b>Facultad:</b> {profile['facultad']}", body_style),
            Paragraph(f"<b>Especialidad:</b> {profile['especialidad']}", body_style),
            Paragraph(f"<b>Modalidad:</b> {profile['modalidad']}", body_style),
            Paragraph(
                f"<b>Plan de estudios:</b> {profile['plan_version']} ({profile['plan_anio']})",
                body_style,
            ),
            Paragraph(f"<b>Semestre académico actual:</b> {profile['semestre_actual']}", body_style),
            Spacer(1, 0.2 * inch),
        ]

    @classmethod
    def _build_constancia_estudios(cls, solicitud, body_style):
        matricula = cls._latest_matricula(solicitud.estudiante_id)
        estado_matricula = matricula.estado if matricula else "sin matrícula registrada"
        periodo = (
            matricula.periodo_academico.semestre
            if matricula and matricula.periodo_academico
            else "—"
        )

        content = [
            Paragraph(
                "Por medio del presente documento se certifica que el/la estudiante "
                f"<b>{cls._student_name(solicitud)}</b>, identificado(a) con DNI "
                f"<b>{cls._student_dni(solicitud)}</b>, se encuentra registrado(a) "
                "en nuestra institución y mantiene condición de estudiante activo(a) "
                "en la especialidad indicada.",
                body_style,
            ),
            Spacer(1, 0.1 * inch),
            Paragraph(f"<b>Periodo académico de referencia:</b> {periodo}", body_style),
            Paragraph(f"<b>Estado de matrícula:</b> {estado_matricula}", body_style),
        ]

        cursos = cls._matricula_courses(matricula)
        if cursos:
            rows = [["Curso", "Sección", "Estado del curso"]]
            for detalle, seccion, curso in cursos:
                rows.append([curso.nombre, seccion.nombre, detalle.estado_curso])
            table = Table(rows, colWidths=[3.2 * inch, 1.5 * inch, 1.5 * inch])
            table.setStyle(cls._table_style())
            content.extend(
                [
                    Spacer(1, 0.15 * inch),
                    Paragraph("<b>Cursos matriculados en el periodo:</b>", body_style),
                    table,
                ]
            )
        else:
            content.append(
                Paragraph(
                    "<i>No se encontraron cursos matriculados para el periodo de referencia.</i>",
                    body_style,
                )
            )

        return content

    @classmethod
    def _build_constancia_matricula(cls, solicitud, body_style):
        matricula = cls._latest_matricula(solicitud.estudiante_id)
        if not matricula:
            return [
                Paragraph(
                    "No se encontró una matrícula registrada para emitir la constancia.",
                    body_style,
                )
            ]

        periodo = matricula.periodo_academico
        content = [
            Paragraph(
                "Se expide la presente constancia para certificar que el/la estudiante "
                f"<b>{cls._student_name(solicitud)}</b> se encuentra matriculado(a) "
                f"en el periodo académico <b>{periodo.semestre if periodo else '—'}</b>.",
                body_style,
            ),
            Paragraph(f"<b>Estado de matrícula:</b> {matricula.estado}", body_style),
            Paragraph(
                f"<b>Vigencia del periodo:</b> "
                f"{periodo.fecha_inicio.strftime('%d/%m/%Y') if periodo else '—'} - "
                f"{periodo.fecha_fin.strftime('%d/%m/%Y') if periodo else '—'}",
                body_style,
            ),
        ]

        if matricula.validador:
            content.append(
                Paragraph(
                    f"<b>Validado por:</b> "
                    f"{matricula.validador.nombres} {matricula.validador.apellidos}",
                    body_style,
                )
            )

        cursos = cls._matricula_courses(matricula)
        if cursos:
            rows = [["Curso", "Sección", "Estado"]]
            for detalle, seccion, curso in cursos:
                rows.append([curso.nombre, seccion.nombre, detalle.estado_curso])
            table = Table(rows, colWidths=[3.2 * inch, 1.5 * inch, 1.5 * inch])
            table.setStyle(cls._table_style())
            content.extend(
                [
                    Spacer(1, 0.15 * inch),
                    Paragraph("<b>Detalle de cursos matriculados:</b>", body_style),
                    table,
                ]
            )

        return content

    @classmethod
    def _build_certificado_notas(cls, solicitud, body_style):
        matricula = cls._latest_matricula(solicitud.estudiante_id)
        if not matricula or not matricula.periodo_academico:
            return [
                Paragraph(
                    "No se encontró un registro académico con notas para emitir el certificado.",
                    body_style,
                )
            ]

        periodo_id = matricula.periodo_academico_id
        notas = EvaluacionService.listar_notas_estudiante(
            solicitud.estudiante_id,
            periodo_id,
        )

        content = [
            Paragraph(
                "Certificado de notas correspondiente al periodo académico "
                f"<b>{matricula.periodo_academico.semestre}</b>.",
                body_style,
            ),
            Paragraph(f"<b>Estado de matrícula:</b> {matricula.estado}", body_style),
        ]

        if not notas:
            content.append(
                Paragraph(
                    "<i>No se registran calificaciones para el periodo indicado.</i>",
                    body_style,
                )
            )
            return content

        rows = [["Curso", "Sección", "Promedio final", "Estado"]]
        for item in notas:
            promedio = item.get("promedio")
            if promedio is None:
                promedio = item.get("promedio_calculado")
            promedio_text = f"{promedio:.2f}" if promedio is not None else "—"
            estado = "Validado" if item.get("is_validated") else "Pendiente"
            rows.append([item["curso"], item["seccion"], promedio_text, estado])

        table = Table(rows, colWidths=[2.6 * inch, 1.2 * inch, 1.2 * inch, 1.0 * inch])
        table.setStyle(cls._table_style())
        content.extend(
            [
                Spacer(1, 0.15 * inch),
                Paragraph("<b>Registro de calificaciones:</b>", body_style),
                table,
            ]
        )

        return content

    @classmethod
    def _build_general_body(cls, solicitud, body_style):
        """Modelo general para tipos de documento fuera del catálogo por defecto."""
        profile = cls._academic_profile(solicitud)
        matricula = cls._latest_matricula(solicitud.estudiante_id)
        fecha_solicitud = solicitud.fecha_creacion.strftime("%d/%m/%Y") if solicitud.fecha_creacion else "—"

        content = [
            Paragraph(
                "Por medio del presente documento se certifica que el/la estudiante "
                f"<b>{cls._student_name(solicitud)}</b>, identificado(a) con DNI "
                f"<b>{cls._student_dni(solicitud)}</b>, ha solicitado la emisión del "
                f"documento <b>{solicitud.tipo_documento}</b> ante el sistema académico "
                "institucional.",
                body_style,
            ),
            Spacer(1, 0.1 * inch),
            Paragraph(f"<b>Fecha de solicitud:</b> {fecha_solicitud}", body_style),
            Paragraph(f"<b>Facultad:</b> {profile['facultad']}", body_style),
            Paragraph(f"<b>Especialidad:</b> {profile['especialidad']}", body_style),
            Paragraph(f"<b>Semestre académico actual:</b> {profile['semestre_actual']}", body_style),
        ]

        if matricula and matricula.periodo_academico:
            content.append(
                Paragraph(
                    f"<b>Periodo académico de referencia:</b> {matricula.periodo_academico.semestre}",
                    body_style,
                )
            )
            content.append(
                Paragraph(f"<b>Estado de matrícula:</b> {matricula.estado}", body_style)
            )

        content.append(
            Paragraph(
                "El presente documento se emite conforme a los registros oficiales "
                "del sistema y cuenta con código de verificación y firma digital para "
                "su autenticidad.",
                body_style,
            )
        )

        return content

    @classmethod
    def _build_type_specific_body(cls, solicitud, body_style):
        template_key = cls._resolve_template_key(solicitud.tipo_documento)

        if template_key == "certificado_notas":
            return cls._build_certificado_notas(solicitud, body_style)
        if template_key == "constancia_matricula":
            return cls._build_constancia_matricula(solicitud, body_style)
        if template_key == "constancia_estudios":
            return cls._build_constancia_estudios(solicitud, body_style)

        return cls._build_general_body(solicitud, body_style)

    @classmethod
    def _build_security_footer(cls, qr_hash, firma_info, body_style, mono_style, subtitle_style):
        verification_url = cls.build_verification_url(qr_hash)
        content = [
            Spacer(1, 0.2 * inch),
            Paragraph(f"<b>Código de verificación:</b> {qr_hash}", body_style),
            Paragraph(f"<b>Algoritmo de firma:</b> {firma_info['firma_algoritmo']}", body_style),
            Paragraph(f"<b>Huella de clave pública:</b> {firma_info['firma_huella_cert']}", body_style),
            Paragraph(f"<b>Hash del contenido:</b> {firma_info['contenido_hash']}", body_style),
            Spacer(1, 0.15 * inch),
            Paragraph("<b>Firma digital (RSA-PSS / SHA-256):</b>", body_style),
            Paragraph(firma_info["firma_digital"][:96] + "...", mono_style),
            Spacer(1, 0.15 * inch),
            Paragraph(
                "Este documento fue generado automáticamente. "
                "Escanee el código QR para validar su autenticidad y firma digital.",
                body_style,
            ),
            Spacer(1, 0.25 * inch),
        ]

        qr_buffer = cls._build_qr_image(verification_url)
        qr_image = Image(qr_buffer, width=1.6 * inch, height=1.6 * inch)
        qr_table = Table([[qr_image]], colWidths=[6.5 * inch])
        qr_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        content.extend([qr_table, Spacer(1, 0.15 * inch), Paragraph(verification_url, subtitle_style)])
        return content

    @classmethod
    def generate_document(cls, solicitud) -> tuple[str, str, dict]:
        qr_hash = cls.generate_qr_hash()
        firma_info = SignatureService.sign_document(solicitud, qr_hash)
        pdf_filename = f"solicitud-{solicitud.id}.pdf"
        pdf_path = cls._documents_dir() / pdf_filename

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocumentTitle",
            parent=styles["Heading1"],
            alignment=1,
            textColor=colors.HexColor("#1e3a5f"),
            spaceAfter=10,
            fontSize=16,
        )
        subtitle_style = ParagraphStyle(
            "DocumentSubtitle",
            parent=styles["Normal"],
            alignment=1,
            textColor=colors.HexColor("#475569"),
            spaceAfter=16,
            fontSize=10,
        )
        body_style = ParagraphStyle(
            "DocumentBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=15,
            spaceAfter=8,
        )
        mono_style = ParagraphStyle(
            "DocumentMono",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        )

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        content = cls._build_common_header(solicitud, title_style, subtitle_style, body_style)
        content.extend(cls._build_type_specific_body(solicitud, body_style))
        content.extend(cls._build_security_footer(qr_hash, firma_info, body_style, mono_style, subtitle_style))

        doc.build(content)

        # Guardar ruta relativa: la URL absoluta del QR ya va dentro del PDF
        return f"/api/documentos/solicitudes/{solicitud.id}/archivo", qr_hash, firma_info

    @classmethod
    def get_pdf_path(cls, solicitud_id: int) -> Path | None:
        pdf_path = cls._documents_dir() / f"solicitud-{solicitud_id}.pdf"
        return pdf_path if pdf_path.exists() else None
