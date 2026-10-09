from contextlib import asynccontextmanager

from fastapi import FastAPI
import sys
from pathlib import Path
from redis_fastapi import FastAPIRedis, cache

from src.init import redis_manager

sys.path.append(str(Path(__file__).parent.parent))

from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.config import settings
from src.database import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    yield
    await redis_manager.close()


app = FastAPI()
FastAPIRedis(app).lifespan().caching()

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)

