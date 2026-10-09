from sqlalchemy import select, insert, delete

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import FacilitiesCreate


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityDataMapper

    async def get_all(self) -> list[FacilitiesOrm]:
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, title: FacilitiesCreate) -> FacilitiesOrm:
        stmt = insert(self.model).values(title=title).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get(self, facility_id: int) -> FacilitiesOrm:
        query = select(self.model).filter_by(id=facility_id)
        result = await self.session.execute(query)
        return result.scalars().one()


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm

    async def get_room_facilities(self, room_id: int) -> list[int]:
        stmt = (
            select(self.model.facilities_id)
            .where(self.model.room_id == room_id)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def delete_room_facilities(
            self,
            room_id: int,
            delete_facilities_ids: set[int],
    ):
        stmt = (
            delete(self.model)
            .where(
                self.model.room_id == room_id,
                self.model.facilities_id.in_(delete_facilities_ids),
            )
        )

        await self.session.execute(stmt)

    async def delete_room_facilities_all(
            self,
            room_id: int,
    ):
        stmt = (
            delete(self.model)
            .where(
                self.model.room_id == room_id
            )
        )

        await self.session.execute(stmt)

