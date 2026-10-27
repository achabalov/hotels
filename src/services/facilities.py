from src.schemas.facilities import Facilities
from src.services.base import BaseService


class FacilitiesService(BaseService):
    async def get_all_facilities(self):
        data = await self.db.facilities.get_all()
        return [Facilities.model_validate(item) for item in data]

    async def get_facility(self, facility_id: int):
        data = await self.db.facilities.get(facility_id)
        return Facilities.model_validate(data)

    async def create_facility(self, title: str):
        facility = await self.db.facilities.create(title)
        await self.db.commit()

        return Facilities.model_validate(facility)