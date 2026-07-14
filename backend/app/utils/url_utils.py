from flask import current_app


def public_api_url(path: str) -> str:
    """Construye una URL absoluta del backend para recursos expuestos por la API."""
    base = current_app.config["PUBLIC_BASE_URL"].rstrip("/")
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base}{path}"
