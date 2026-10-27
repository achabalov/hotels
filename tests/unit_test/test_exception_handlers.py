import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy.exc import DataError, IntegrityError, NoResultFound, OperationalError

from src.api.exception_handlers import register_exception_handlers
from src.exceptions import (
    AuthenticationError,
    ConflictError,
    ImageStorageError,
    ImageTooLargeError,
    InvalidImageError,
    NotFoundError,
    UnsupportedImageFormatError,
    validate_dates,
)
from src.repositories.errors import translate_database_error


class ExceptionHandlersTest(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        register_exception_handlers(self.app)
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def assert_error(self, exc, status, detail):
        @self.app.get("/error")
        async def error():
            raise exc

        response = self.client.get("/error")
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.json(), {"detail": detail})

    def test_missing_resource(self):
        self.assert_error(NotFoundError("Номер не найден"), 404, "Номер не найден")

    def test_no_result(self):
        with self.assertLogs("src.api.exception_handlers", level="ERROR"):
            self.assert_error(NoResultFound(), 500, "Внутренняя ошибка сервера")

    def test_booking_conflict(self):
        self.assert_error(ConflictError("Номер занят"), 409, "Номер занят")

    def test_duplicate(self):
        original = Exception("private SQL details")
        original.sqlstate = "23505"
        self.assert_error(
            translate_database_error(IntegrityError("SQL", {}, original)),
            409,
            "Объект с такими данными уже существует",
        )

    def test_unexpected_error_hides_details(self):
        with self.assertLogs("src.api.exception_handlers", level="ERROR"):
            self.assert_error(RuntimeError("secret"), 500, "Внутренняя ошибка сервера")

    def test_invalid_dates(self):
        from datetime import date

        from src.exceptions import AppError

        for end in [date(2027, 1, 1), date(2026, 12, 31)]:
            with self.assertRaises(AppError):
                validate_dates(date(2027, 1, 1), end)

    def test_foreign_key_conflict(self):
        original = Exception("private details")
        original.sqlstate = "23503"
        self.assert_error(
            translate_database_error(IntegrityError("SQL", {}, original)),
            409,
            "Связанный объект не существует или используется другими объектами",
        )

    def test_invalid_database_value(self):
        self.assert_error(
            translate_database_error(DataError("SQL", {}, Exception("private"))),
            422,
            "Недопустимые данные",
        )

    def test_null_database_value(self):
        original = Exception("private")
        original.sqlstate = "23502"
        self.assert_error(
            translate_database_error(IntegrityError("SQL", {}, original)),
            422,
            "Недопустимые данные",
        )

    def test_database_unavailable(self):
        with self.assertLogs("src.api.exception_handlers", level="ERROR"):
            self.assert_error(
                OperationalError("SQL", {}, Exception("private")), 503, "Сервис временно недоступен"
            )

    def test_database_connection_refused(self):
        with self.assertLogs("src.api.exception_handlers", level="ERROR"):
            self.assert_error(ConnectionRefusedError("private"), 503, "Сервис временно недоступен")

    def test_redis_unavailable(self):
        with self.assertLogs("src.api.exception_handlers", level="ERROR"):
            self.assert_error(RedisConnectionError("private"), 503, "Сервис временно недоступен")

    def test_untranslated_database_error_is_internal(self):
        original = Exception("private SQL details")
        original.sqlstate = "23505"
        with self.assertLogs("src.api.exception_handlers", level="ERROR"):
            self.assert_error(IntegrityError("SQL", {}, original), 500, "Внутренняя ошибка сервера")

    def test_authentication_error(self):
        self.assert_error(AuthenticationError("Токен истек"), 401, "Токен истек")

    def test_invalid_image(self):
        self.assert_error(InvalidImageError("Файл пуст"), 422, "Файл пуст")

    def test_large_image(self):
        self.assert_error(ImageTooLargeError("Слишком большой файл"), 413, "Слишком большой файл")

    def test_unsupported_image(self):
        self.assert_error(UnsupportedImageFormatError("Формат"), 415, "Формат")

    def test_image_storage_error(self):
        self.assert_error(ImageStorageError("Хранилище недоступно"), 503, "Хранилище недоступно")
