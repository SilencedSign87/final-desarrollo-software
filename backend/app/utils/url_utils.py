import os

from flask import current_app, has_request_context, request


def _is_local_base(url: str) -> bool:
    lowered = (url or "").lower()
    return "127.0.0.1" in lowered or "localhost" in lowered


def public_api_url(path: str) -> str:
    """Construye una URL absoluta del backend para recursos expuestos por la API."""
    if not path.startswith("/"):
        path = f"/{path}"

    base = (
        os.environ.get("PUBLIC_BASE_URL")
        or current_app.config.get("PUBLIC_BASE_URL")
        or ""
    ).rstrip("/")

    # Si falta la variable o quedó en localhost, usar el host real de la petición
    # (en Render funciona con ProxyFix en create_app).
    if (not base or _is_local_base(base)) and has_request_context():
        root = request.url_root.rstrip("/")
        if root and not _is_local_base(root):
            base = root
        elif not base:
            base = root

    if not base:
        base = "http://127.0.0.1:5000"

    return f"{base}{path}"
