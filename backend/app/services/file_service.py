import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class FileService:
    @staticmethod
    def _comprobantes_dir() -> Path:
        folder = Path(current_app.config["COMPROBANTES_FOLDER"])
        if not folder.is_absolute():
            folder = Path(current_app.root_path).parent / folder
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def _extension(filename: str) -> str:
        if "." not in filename:
            raise ValueError("El archivo debe tener una extensión válida")
        return filename.rsplit(".", 1)[1].lower()

    @classmethod
    def validate_comprobante(cls, file_storage):
        if file_storage is None or not file_storage.filename:
            raise ValueError("Debes adjuntar el comprobante de pago")

        ext = cls._extension(file_storage.filename)
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Formato no permitido. Usa PDF, PNG, JPG o WEBP"
            )

        file_storage.stream.seek(0, 2)
        size = file_storage.stream.tell()
        file_storage.stream.seek(0)
        if size > MAX_FILE_SIZE:
            raise ValueError("El comprobante no puede superar los 5 MB")

        return ext

    @classmethod
    def save_comprobante(cls, file_storage, prefix: str) -> str:
        """Guarda el archivo y retorna el nombre relativo almacenado."""
        ext = cls.validate_comprobante(file_storage)
        safe_prefix = secure_filename(prefix) or "comprobante"
        filename = f"{safe_prefix}-{uuid.uuid4().hex[:12]}.{ext}"
        path = cls._comprobantes_dir() / filename
        file_storage.save(path)
        return filename

    @classmethod
    def get_comprobante_path(cls, stored_name: str) -> Path | None:
        if not stored_name:
            return None
        # Compatibilidad: si se guardó una URL API, no es un archivo local
        if stored_name.startswith("http") or stored_name.startswith("/api/"):
            return None
        path = cls._comprobantes_dir() / Path(stored_name).name
        return path if path.exists() else None

    @staticmethod
    def mimetype_for(filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }.get(ext, "application/octet-stream")
