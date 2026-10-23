import asyncio
import logging
import sys
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI
from redis_fastapi import FastAPIRedis

from src.api.dependencies import get_db
from src.api.exception_handlers import register_exception_handlers
from src.init import redis_manager

sys.path.append(str(Path(__file__).parent.parent))

from src.api.auth import router as router_auth
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.hotels import router as router_hotels
from src.api.images import router as router_images
from src.api.rooms import router as router_rooms
from src.database import *


async def get_bookings_today_checkin():
    async for db in get_db():
        bookings = await db.bookings.get_bookings_with_today_checkin()
        print(f"Bookings: {bookings}")


async def run_send_email_always():
    while True:
        try:
            await get_bookings_today_checkin()
        except Exception:
            logging.getLogger(__name__).exception("Failed to check today bookings")
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    task = asyncio.create_task(run_send_email_always())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        await redis_manager.close()


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
FastAPIRedis(app).lifespan().caching()

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.include_router(router_images)
