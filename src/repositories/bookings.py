from datetime import date

from sqlalchemy import select

from src.exceptions import ConflictError, NotFoundError, validate_dates
from src.models import RoomsOrm
from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.ustils import get_ids_for_booking
from src.schemas.bookings import BookingsAdd


class BookingRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    # async def add_bookings(self, data: BookingsAdd):
    #     add_data_stmt = (
    #         insert(self.model)
    #         .values(**data.model_dump())
    #         .returning(self.model)
    #     )
    #
    #     stmt = await self._execute(add_data_stmt)
    #
    #     return stmt.scalars().one()

    async def add_bookings(self, data: BookingsAdd):
        validate_dates(data.date_from, data.date_to)
        rooms_response = select(RoomsOrm).filter_by(id=data.room_id).with_for_update()
        hotel = await self._execute(rooms_response)
        room = hotel.scalars().first()
        if room is None:
            raise NotFoundError("Номер не найден")
        hotel_id = room.hotel_id
        rooms_ids_to_get = get_ids_for_booking(
            date_from=data.date_from, date_to=data.date_to, hotel_id=hotel_id
        )

        rooms_ids_to_book_res = await self._execute(rooms_ids_to_get)
        rooms_ids_to_book: list[int] = rooms_ids_to_book_res.scalars().all()
        if data.room_id in rooms_ids_to_book:
            return await self.add(data)
        else:
            raise ConflictError("На выбранные даты нет свободных номеров")

    async def get_bookings(self):
        query = select(self.model)
        result = await self._execute(query)
        return result.scalars().all()

    async def get_bookings_me(self, user_id: int):
        query = select(self.model).filter_by(user_id=user_id)
        result = await self._execute(query)
        return result.scalars().all()

    async def get_bookings_with_today_checkin(self):
        query = select(self.model).filter(self.model.date_from == date.today())
        result = await self._execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in result.scalars().all()]
