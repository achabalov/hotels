
from sqlalchemy import insert, select

from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.schemas.bookings import BookingsCreate


class BookingRepository(BaseRepository):
    model = BookingsOrm

    async def add_bookings(self, user_id, price, data: BookingsCreate):
        add_data_stmt = insert(self.model).values(price=price, user_id=user_id, **data.model_dump()).returning(self.model)
        stmt = await self.session.execute(add_data_stmt)
        return stmt.scalars().one()

    async def get_bookings(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bookings_me(self, user_id: int):
        query = select(self.model).filter_by(user_id=user_id)
        result = await self.session.execute(query)
        return result.scalars().all()