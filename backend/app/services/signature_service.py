from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from flask import current_app


class SignatureService:
    """Firma digital RSA institucional para documentos emitidos."""

    @staticmethod
    def _keys_dir() -> Path:
        folder = Path(current_app.root_path).parent / "instance" / "keys"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @classmethod
    def _private_key_path(cls) -> Path:
        return cls._keys_dir() / "document_signing_key.pem"

    @classmethod
    def _public_key_path(cls) -> Path:
        return cls._keys_dir() / "document_signing_key.pub.pem"

    @classmethod
    def _ensure_keys(cls):
        private_path = cls._private_key_path()
        public_path = cls._public_key_path()

        if private_path.exists() and public_path.exists():
            return

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        private_path.write_bytes(private_bytes)
        public_path.write_bytes(public_bytes)

    @classmethod
    def _load_private_key(cls):
        cls._ensure_keys()
        return serialization.load_pem_private_key(
            cls._private_key_path().read_bytes(),
            password=None,
        )

    @classmethod
    def _load_public_key(cls):
        cls._ensure_keys()
        return serialization.load_pem_public_key(cls._public_key_path().read_bytes())

    @staticmethod
    def build_payload(solicitud, qr_hash: str) -> bytes:
        parts = [
            solicitud.codigo_ticket or str(solicitud.id),
            solicitud.tipo_documento,
            str(solicitud.estudiante_id),
            qr_hash,
            "emitido",
        ]
        return "|".join(parts).encode("utf-8")

    @classmethod
    def content_hash(cls, solicitud, qr_hash: str) -> str:
        digest = hashes.Hash(hashes.SHA256())
        digest.update(cls.build_payload(solicitud, qr_hash))
        return digest.finalize().hex()

    @classmethod
    def sign_document(cls, solicitud, qr_hash: str) -> dict:
        private_key = cls._load_private_key()
        payload = cls.build_payload(solicitud, qr_hash)
        signature = private_key.sign(
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return {
            "firma_digital": signature.hex(),
            "firma_algoritmo": "RSA-PSS-SHA256",
            "firma_huella_cert": cls.fingerprint(),
            "contenido_hash": cls.content_hash(solicitud, qr_hash),
        }

    @classmethod
    def verify_signature(cls, solicitud, qr_hash: str, firma_hex: str) -> bool:
        if not firma_hex:
            return False
        try:
            public_key = cls._load_public_key()
            payload = cls.build_payload(solicitud, qr_hash)
            public_key.verify(
                bytes.fromhex(firma_hex),
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    @classmethod
    def fingerprint(cls) -> str:
        public_key = cls._load_public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        digest = hashes.Hash(hashes.SHA256())
        digest.update(public_bytes)
        return digest.finalize().hex()[:16]
