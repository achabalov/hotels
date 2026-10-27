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
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import TimeoutError as DatabaseTimeoutError

from src.exceptions import (
    AppError,
    AuthenticationError,
    ConflictError,
    ImageStorageError,
    ImageTooLargeError,
    InvalidDataError,
    NotFoundError,
    UnsupportedImageFormatError,
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        status_codes = {
            NotFoundError: 404,
            ConflictError: 409,
            InvalidDataError: 422,
            AuthenticationError: 401,
            ImageTooLargeError: 413,
            UnsupportedImageFormatError: 415,
            ImageStorageError: 503,
        }
        status_code = next(
            (status_codes[cls] for cls in type(exc).__mro__ if cls in status_codes),
            400,
        )
        return JSONResponse(status_code=status_code, content={"detail": exc.detail})

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
