from sqlalchemy.exc import DataError, IntegrityError

from src.exceptions import ConflictError, InvalidDataError


def translate_database_error(exc):
    """Translate known constraint failures; unexpected failures keep their traceback."""
    if isinstance(exc, DataError):
        return InvalidDataError("Недопустимые данные")
    if isinstance(exc, IntegrityError):
        code = getattr(exc.orig, "sqlstate", None)
        if code == "23505":
            return ConflictError("Объект с такими данными уже существует")
        if code == "23503":
            return ConflictError(
                "Связанный объект не существует или используется другими объектами"
            )
        if code in {"23502", "23514"}:
            return InvalidDataError("Недопустимые данные")
    return None
