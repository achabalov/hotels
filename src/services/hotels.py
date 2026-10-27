from datetime import date

from src.api.dependencies import PaginationDep
from src.exceptions import validate_dates
from src.schemas.hotels import HotelAdd, HotelPatch
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_filtered_by_date(
            self,
            date_from: date,
            date_to: date,
            pagination: PaginationDep,
            location: str | None = None,
            title: str | None = None,
    ):
        validate_dates(date_from, date_to)
        per_page = pagination.per_page or 5

        return await self.db.hotels.get_filtered_by_date(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=pagination.per_page or 5,
            offset=(pagination.page - 1) * per_page,
        )

    async def get_hotel(self, hotel_id: int):
        return await self.db.hotels.get_one_or_none(id=hotel_id)

    async def create_hotel(self, hotel_data: HotelAdd):
        get_data_stmt = await self.db.hotels.add(hotel_data)
        await self.db.commit()
        return get_data_stmt

    async def update_hotel(self, hotel_id: int, exclude_unset: bool, data: HotelAdd | HotelPatch):
        await self.db.hotels.update(data, exclude_unset=exclude_unset, id=hotel_id)
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int):
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()