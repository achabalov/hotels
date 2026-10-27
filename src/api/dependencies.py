from typing import Annotated

from fastapi import Depends, HTTPException, Path, Query, Request
from pydantic import BaseModel
from redis_fastapi import cache, cache_evict, cache_put

from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager

PositiveId = Annotated[int, Path(gt=0)]


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1)]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Токен отсутствует")
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    payload = AuthService().decode_token(token=token)
    user_id = payload.get("user_id")
    if type(user_id) is not int or user_id <= 0:
        raise HTTPException(status_code=401, detail="Некорректный токен")
    return user_id


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


async def get_authenticated_user_id(
    db: DBDep, user_id: Annotated[int, Depends(get_current_user_id)]
):
    if await db.users.get_one_or_none(id=user_id) is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user_id


UserIdDep = Annotated[int, Depends(get_authenticated_user_id)]


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
