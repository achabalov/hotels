from datetime import date
from fastapi import HTTPException
from sqlalchemy import select

from src.database import session
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
    #     stmt = await self.session.execute(add_data_stmt)
    #
    #     return stmt.scalars().one()


    async def add_bookings(self, data: BookingsAdd):
        rooms_response = select(RoomsOrm).filter_by(id=data.room_id)
        hotel = await session.execute(rooms_response)
        hotel_id = hotel.scalars().first().hotel_id
        rooms_ids_to_get = get_ids_for_booking(date_from=data.date_from, date_to=data.date_to, hotel_id=hotel_id)

        rooms_ids_to_book_res = await session.execute(rooms_ids_to_get)
        rooms_ids_to_book: list[int] = rooms_ids_to_book_res.scalars().all()
        if data.room_id in rooms_ids_to_book:
            return await self.add(data)
        else:
            raise HTTPException(status_code=500, detail="Room is beasy")

    async def get_bookings(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bookings_me(self, user_id: int):
        query = select(self.model).filter_by(user_id=user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bookings_with_today_checkin(self):
        query = select(self.model).filter(self.model.date_from == date.today())
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in result.scalars().all()]
