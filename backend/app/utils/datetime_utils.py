from datetime import datetime, timedelta, timezone

# Perú no usa horario de verano; evita ZoneInfo/tzdata en Windows.
LIMA_TZ = timezone(timedelta(hours=-5))


def utc_now_naive() -> datetime:
    """UTC actual sin tzinfo (evita conversiones raras de SQLAlchemy/SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_lima(dt: datetime | None) -> str:
    """Formatea un datetime guardado en UTC a hora de Perú para mostrar en UI."""
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.astimezone(LIMA_TZ).strftime("%d/%m/%Y, %H:%M:%S")
