from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from src.config import settings
from src.exceptions import InvalidTokenError, TokenExpiredError
from src.services.base import BaseService


class AuthService(BaseService):
    password_hash = PasswordHash.recommended()

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()

        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredError("Токен истек") from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError("Некорректный токен") from exc
