from src.exceptions import validate_dates, NotFoundError
from src.schemas.bookings import BookingsAddRequest, BookingsAdd
from src.services.base import BaseService


class BookingService(BaseService):

    async def get_all_bookings(self):
        bookings = await self.db.bookings.get_bookings()
        return bookings

    async def get_my_bookings(self, user_id: int):
        result = await self.db.bookings.get_bookings_me(user_id=user_id)
        return result

    async def create_booking(self, data: BookingsAddRequest, user_id: int):
        validate_dates(data.date_from, data.date_to)
        room = await self.db.rooms.get_room(id=data.room_id)
        if room is None:
            raise NotFoundError("Номер не найден")
        room_price: int = room.price
        booking_data = BookingsAdd(
            **data.model_dump(),
            user_id=user_id,
            price=room_price,
        )

        result = await self.db.bookings.add_bookings(booking_data)

        await self.db.commit()

        return result