from datetime import date

from sqlalchemy import select, insert, delete, update

from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.ustils import get_ids_for_booking
from src.schemas.rooms import RoomCreate, RoomsPatch


class RoomsRepository(BaseRepository):
    model = RoomsOrm

    async def get_room(self, **filtered):
        query = select(self.model).filter_by(**filtered)

        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_filtered_by_date(self, date_from: date, date_to: date, hotel_id: int):
        rooms_ids_to_get = get_ids_for_booking(date_from, date_to, hotel_id)
        result = await self.get_filtered(RoomsOrm.id.in_(rooms_ids_to_get))
        return result


    async def get_all(self):
        query = select(self.model)

        result = await self.session.execute(query)
        return result.scalars().all()


    async def create_room(self, data: RoomCreate, hotel_id: int):
        add_data_stmt = insert(self.model).values(hotel_id=hotel_id, **data.model_dump(exclude={"facilities_ids"})).returning(self.model)
        stmt = await self.session.execute(add_data_stmt)
        return stmt.scalars().one()


    async def delete_room(self, **filter):
        delete_room = delete(self.model).filter_by(**filter).returning(self.model)
        result = await self.session.execute(delete_room)
        return result.scalars().one_or_none()


    async def update(self, room: RoomsPatch, exclude_unset: bool, **filter_by):
        update_data = update(self.model).filter_by(**filter_by).values(
            **room.model_dump(exclude_unset=exclude_unset)).returning(self.model)
        result = await self.session.execute(update_data)
        return result.scalars().one_or_none()
