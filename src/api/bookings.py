from fastapi import APIRouter

from src.api.dependencies import UserIdDep, DBDep
from src.schemas.bookings import BookingsCreate, Bookings, BookingsAdd, BookingsAddRequest

router = APIRouter(prefix='/bookings', tags=['Бронирование>'])


@router.get('', response_model=list[Bookings])
async def get_bookings(db: DBDep):
    result = await db.bookings.get_bookings()
    return result

@router.get('/me')
async def get_bookings_me(user_id: UserIdDep, db: DBDep):
    result = await db.bookings.get_bookings_me(user_id=user_id)
    return result

@router.post("", response_model=Bookings)
async def add_bookings(
    user: UserIdDep,
    db: DBDep,
    data: BookingsAddRequest,
):
    room = await db.rooms.get_room(id=data.room_id)
    room_price: int = room.price
    booking_data = BookingsAdd(
        **data.model_dump(),
        user_id=user,
        price=room_price,
    )

    result = await db.bookings.add_bookings(booking_data)

    await db.session.commit()

    return result