from typing import Annotated
from jwt.exceptions import ExpiredSignatureError
from fastapi import Depends, Query, Request, HTTPException
from redis_fastapi import cache, default_key_builder, cache_put, cache_evict
from pydantic import BaseModel

from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1)]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    token = request.cookies.get('access_token', None)
    if not token:
        raise HTTPException(status_code=401, detail='Token is missing')
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    try:
        token = AuthService().decode_token(token=token)
        return token['user_id']
    except ExpiredSignatureError as e:
        raise HTTPException(401, "Токен истек")


UserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def cached(ttl: int = 60, group: str = ""):
    return Depends(
        cache(
            ttl=ttl,
            eviction_group=group,
        )
    )


def cache_clear(group: str):
    return Depends(
        cache_evict(
            eviction_group=group,
        )
    )


def cache_update(ttl: int = 60, group: str = ""):
    return Depends(
        cache_put(
            ttl=ttl,
            eviction_group=group,
        )
    )
