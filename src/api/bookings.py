from fastapi import APIRouter

from src.api.dependencies import UserIdDep, DBDep
from src.schemas.bookings import BookingsCreate, BookingsResponse, Bookings

router = APIRouter(prefix='/bookings', tags=['Бронирование>'])



@router.get('/', response_model=list[Bookings])
async def get_bookings(db: DBDep):
    result = await db.bookings.get_bookings()
    return result

@router.get('/me')
async def get_bookings_me(user_id: UserIdDep, db: DBDep):
    result = await db.bookings.get_bookings_me(user_id=user_id)
    return result

@router.post('/', response_model=Bookings)
async def add_bookings(user: UserIdDep, db: DBDep, data: BookingsCreate):
    room = await db.rooms.get_room(id=data.room_id)
    result = await db.bookings.add_bookings(user_id=user, price=room.price, data=data)
    await db.session.commit()
    return result
