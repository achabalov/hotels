from sqlalchemy import select, insert
from fastapi import Body

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepository
from src.schemas.facilities import FacilitiesAdd


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm

    async def get_all(self) -> list[FacilitiesAdd]:
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, title: str = Body()):
        stmt = insert(self.model).values(title=title).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar()


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm