import json
from pathlib import Path
from unittest import mock

mock.patch("src.api.dependencies.cache", lambda *args, **kwargs: lambda: None).start()
mock.patch('src.api.dependencies.cache_put', lambda *args, **kwargs: lambda: None).start()
mock.patch('src.api.dependencies.cache_evict', lambda *args, **kwargs: lambda: None).start()

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, MetaData, String, Table

from src.config import settings
from src.database import Base, engine_null_pull, null_pull_session_maker
from src.main import app
from src.schemas.facilities import FacilitiesCreate, RoomFacilitiesCreate
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomCreate
from src.utils.db_manager import DBManager

meta = MetaData()
t1 = Table("t1", meta, Column("name", String(50), primary_key=True))
BASE_DIR = Path(__file__).parent


@pytest.fixture(scope='session', autouse=True)
async def check_test_mode() -> None:
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def lifespan():
    async with LifespanManager(app):
        yield


@pytest.fixture(scope="session")
async def ac(lifespan) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(scope='session')
async def db() -> DBManager:
    async with DBManager(session_factory=null_pull_session_maker) as db:
        yield db


@pytest.fixture(scope='session', autouse=True)
async def create_user(ac, init_db):
    await ac.post("auth/register", json={"email":"cot@pes.ru", "password":"12345"})

@pytest.fixture(scope='session')
async def authenticated_ac(create_user, ac):
    res = await ac.post("auth/login", json={"email":"cot@pes.ru", "password":"12345"})
    assert res.status_code == 200
    token = res.json()['access_token']
    assert token
    assert res.cookies['access_token']
    assert res.cookies['access_token'] == token
    assert isinstance(token, str)

    yield ac


@pytest.fixture(scope='session', autouse=True)
async def init_db(check_test_mode) :
    async with engine_null_pull.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


    with open(BASE_DIR / "facilities.json", 'r', encoding='utf-8') as file: # noqa
        facilities = json.load(file)

    with open(BASE_DIR / "hotels.json", 'r', encoding='utf-8') as file: # noqa
        hotels = json.load(file)

    with open(BASE_DIR / 'rooms.json', 'r', encoding='utf-8') as file: # noqa
        rooms_data = json.load(file)

    facilities = [FacilitiesCreate.model_validate(f) for f in facilities]
    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels]
    async with DBManager(session_factory=null_pull_session_maker) as db_:

        await db_.facilities.add_bulk(facilities)
        await db_.hotels.add_bulk(hotels)

        for room in rooms_data:
            hotel_id = room.pop("hotel_id")

            room_data = RoomCreate.model_validate(room)

            facilities_ids = room_data.facilities_ids or []

            created_room = await db_.rooms.create_room(
                room_data,
                hotel_id=hotel_id
            )

            rooms_facilities_data = [
                RoomFacilitiesCreate(
                    room_id=created_room.id,
                    facilities_id=f_id
                )
                for f_id in facilities_ids
            ]
        await db_.rooms_facilities.add_bulk(rooms_facilities_data)
        await db_.commit()

