from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import (
    Bookings,
    BookingsAddRequest,
)
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование>"])


@router.get("", response_model=list[Bookings])
async def get_bookings(db: DBDep):
    bookings = await BookingService(db).get_all_bookings()
    return bookings


@router.get("/me")
async def get_bookings_me(user_id: UserIdDep, db: DBDep):
    result = await BookingService(db).get_my_bookings(user_id)
    return result


@router.post("", response_model=Bookings)
async def add_bookings(
    user_id: UserIdDep,
    db: DBDep,
    data: BookingsAddRequest,
):
    booking = await BookingService(db).create_booking(data=data, user_id=user_id)
    return booking