import logging

from asyncpg.exceptions import (
    CannotConnectNowError,
    PostgresConnectionError,
    TooManyConnectionsError,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from kombu.exceptions import OperationalError as BrokerError
from redis.exceptions import RedisError
from sqlalchemy.exc import DataError, IntegrityError, NoResultFound, OperationalError
from sqlalchemy.exc import TimeoutError as DatabaseTimeoutError

from src.exceptions import AppError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(NoResultFound)
    async def not_found_handler(request: Request, exc: NoResultFound):
        return JSONResponse(status_code=404, content={"detail": "Объект не найден"})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        code = getattr(exc.orig, "sqlstate", None)
        if code == "23505":
            detail = "Объект с такими данными уже существует"
        elif code == "23503":
            detail = "Связанный объект не существует или используется другими объектами"
        elif code in {"23502", "23514"}:
            return JSONResponse(status_code=422, content={"detail": "Недопустимые данные"})
        else:
            logger.error("Database integrity error", exc_info=exc)
            return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})
        return JSONResponse(status_code=409, content={"detail": detail})

    @app.exception_handler(DataError)
    async def data_error_handler(request: Request, exc: DataError):
        return JSONResponse(status_code=422, content={"detail": "Недопустимые данные"})

    @app.exception_handler(ConnectionError)
    @app.exception_handler(TimeoutError)
    @app.exception_handler(PostgresConnectionError)
    @app.exception_handler(CannotConnectNowError)
    @app.exception_handler(TooManyConnectionsError)
    @app.exception_handler(OperationalError)
    @app.exception_handler(DatabaseTimeoutError)
    @app.exception_handler(RedisError)
    @app.exception_handler(BrokerError)
    async def unavailable_handler(request: Request, exc: Exception):
        logger.error("Service unavailable: %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(status_code=503, content={"detail": "Сервис временно недоступен"})

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        logger.error("Unhandled error: %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})
