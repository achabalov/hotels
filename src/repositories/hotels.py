from datetime import date

from sqlalchemy import select, func

from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository, BaseModel
from src.repositories.ustils import get_ids_for_booking
from src.schemas.hotels import Hotel


class HotelRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

    async def get_filtered_by_date(self, date_from: date, date_to: date, location, title, limit, offset) -> list[Hotel]:
        rooms_ids_to_get = get_ids_for_booking(date_from=date_from, date_to=date_to)

        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.lower().strip()))
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.lower().strip()))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()