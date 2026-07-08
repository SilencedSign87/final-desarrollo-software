import io
import secrets
from datetime import datetime, timezone
from pathlib import Path

import qrcode
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class DocumentService:
    @staticmethod
    def _documents_dir() -> Path:
        folder = Path(current_app.config["DOCUMENTS_FOLDER"])
        if not folder.is_absolute():
            folder = Path(current_app.root_path).parent / folder
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def build_verification_url(qr_hash: str) -> str:
        base_url = current_app.config["PUBLIC_BASE_URL"].rstrip("/")
        return f"{base_url}/api/documentos/verificar/{qr_hash}"

    @staticmethod
    def build_download_url(solicitud_id: int) -> str:
        return f"/api/documentos/solicitudes/{solicitud_id}/archivo"

    @staticmethod
    def generate_qr_hash() -> str:
        return secrets.token_hex(16)

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
    def _student_program(solicitud) -> str:
        plan = solicitud.estudiante.plan_estudio
        especialidad = plan.especialidad.nombre if plan and plan.especialidad else "No registrada"
        return especialidad

    @classmethod
    def generate_document(cls, solicitud) -> tuple[str, str]:
        qr_hash = cls.generate_qr_hash()
        verification_url = cls.build_verification_url(qr_hash)
        pdf_filename = f"solicitud-{solicitud.id}.pdf"
        pdf_path = cls._documents_dir() / pdf_filename

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocumentTitle",
            parent=styles["Heading1"],
            alignment=1,
            textColor=colors.HexColor("#1e3a5f"),
            spaceAfter=16,
        )
        subtitle_style = ParagraphStyle(
            "DocumentSubtitle",
            parent=styles["Normal"],
            alignment=1,
            textColor=colors.HexColor("#475569"),
            spaceAfter=24,
        )
        body_style = ParagraphStyle(
            "DocumentBody",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
            spaceAfter=10,
        )

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        issued_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
        student_name = cls._student_name(solicitud)
        student_dni = cls._student_dni(solicitud)
        student_program = cls._student_program(solicitud)

        content = [
            Paragraph("Sistema Académico Universitario", title_style),
            Paragraph("Documento oficial emitido", subtitle_style),
            Spacer(1, 0.2 * inch),
            Paragraph(f"<b>Tipo de documento:</b> {solicitud.tipo_documento}", body_style),
            Paragraph(f"<b>Estudiante:</b> {student_name}", body_style),
            Paragraph(f"<b>DNI:</b> {student_dni}", body_style),
            Paragraph(f"<b>Programa:</b> {student_program}", body_style),
            Paragraph(f"<b>Fecha de emisión:</b> {issued_at}", body_style),
            Paragraph(f"<b>Código de verificación:</b> {qr_hash}", body_style),
            Spacer(1, 0.3 * inch),
            Paragraph(
                "Este documento fue generado automáticamente por el sistema académico. "
                "Escanee el código QR para validar su autenticidad.",
                body_style,
            ),
            Spacer(1, 0.4 * inch),
        ]

        qr_buffer = cls._build_qr_image(verification_url)
        qr_image = Image(qr_buffer, width=1.8 * inch, height=1.8 * inch)
        qr_table = Table([[qr_image]], colWidths=[6.5 * inch])
        qr_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        content.extend([qr_table, Spacer(1, 0.2 * inch), Paragraph(verification_url, subtitle_style)])

        doc.build(content)

        return cls.build_download_url(solicitud.id), qr_hash

    @classmethod
    def get_pdf_path(cls, solicitud_id: int) -> Path | None:
        pdf_path = cls._documents_dir() / f"solicitud-{solicitud_id}.pdf"
        return pdf_path if pdf_path.exists() else None
