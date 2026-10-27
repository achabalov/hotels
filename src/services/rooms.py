from datetime import date

from src.exceptions import NotFoundError, validate_dates
from src.repositories.mappers.mappers import RoomDataWithRelsMapper
from src.schemas.facilities import RoomFacilitiesCreate
from src.schemas.rooms import RoomCreate, RoomsPatch
from src.services.base import BaseService


class RoomsService(BaseService):
    async def validate_facilities(self, facility_ids: list[int]):
        for facility_id in set(facility_ids):
            if await self.db.facilities.get_one_or_none(id=facility_id) is None:
                raise NotFoundError(f"Удобство {facility_id} не найдено")

    async def sync_facilities(self,  room_id: int, new_facility_ids: list[int]):
        await self.validate_facilities(new_facility_ids)
        current_facility_ids = set(await self.db.rooms_facilities.get_room_facilities(room_id))
        new_facility_ids = set(new_facility_ids)
        facility_ids_to_add = new_facility_ids - current_facility_ids
        facility_ids_to_delete = current_facility_ids - new_facility_ids
        if facility_ids_to_delete:
            await self.db.rooms_facilities.delete_room_facilities(
                room_id=room_id, delete_facilities_ids=facility_ids_to_delete
            )

        if facility_ids_to_add:
            facilities_to_add = [
                RoomFacilitiesCreate(room_id=room_id, facilities_id=f_id)
                for f_id in facility_ids_to_add
            ]
            await self.db.rooms_facilities.add_bulk(facilities_to_add)

    async def get_room(self, hotel_id: int, room_id: int):
        room = await self.db.rooms.get_room(hotel_id=hotel_id, id=room_id)
        if room is None:
            raise NotFoundError("Номер не найден")
        return RoomDataWithRelsMapper.map_to_domain_entity(room)

    async def get_rooms(self, hotel_id: int, date_from: date, date_to: date):
        if await self.db.hotels.get_one_or_none(id=hotel_id) is None:
            raise NotFoundError("Отель не найден")
        validate_dates(date_from, date_to)
        rooms = await self.db.rooms.get_filtered_by_date(
            date_from=date_from, date_to=date_to, hotel_id=hotel_id
        )
        return rooms

    async def get_all_rooms(self):
        rooms = await self.db.rooms.get_all()
        return [RoomDataWithRelsMapper.map_to_domain_entity(room) for room in rooms]

    async def create_room(self, hotel_id: int, data: RoomCreate):
        if await self.db.hotels.get_one_or_none(id=hotel_id) is None:
            raise NotFoundError("Отель не найден")
        facilities_ids = list(set(data.facilities_ids))
        await self.validate_facilities(facilities_ids)

        room = await self.db.rooms.create_room(data, hotel_id=hotel_id)

        rooms_facilities_data = [
            RoomFacilitiesCreate(room_id=data.id, facilities_id=f_id) for f_id in facilities_ids
        ]
        await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()
        return room

    async def delete_room(self, hotel_id: int, room_id: int):
        room = await self.db.rooms.delete_room(hotel_id=hotel_id, id=room_id)
        if room is None:
            raise NotFoundError("Номер не найден")
        await self.db.commit()
        return room

    async def update_room(self, hotel_id: int, room_id: int, data: RoomCreate):
        if await self.db.rooms.get_room(hotel_id=hotel_id, id=room_id) is None:
            raise NotFoundError("Номер не найден")
        if data.facilities_ids is not None:
            await self.sync_facilities(
                room_id=room_id,
                new_facility_ids=data.facilities_ids,
            )

        result = await self.db.rooms.update(
            data,
            exclude_unset=False,
            id=room_id,
            hotel_id=hotel_id,
        )

        await self.db.commit()

        return result

    async def partial_update_room(self, hotel_id: int, room_id: int, data: RoomsPatch):
        if await self.db.rooms.get_room(hotel_id=hotel_id, id=room_id) is None:
            raise NotFoundError("Номер не найден")
        if data.facilities_ids is not None:
            await self.sync_facilities(
                room_id=room_id,
                new_facility_ids=data.facilities_ids,
            )
        update_data = data.model_dump(
            exclude_unset=True,
            exclude={"facilities_ids", "hotel_id"},
        )
        if update_data:
            await self.db.rooms.update(
                data,
                exclude_unset=True,
                id=room_id,
                hotel_id=hotel_id,
            )

        room = await self.db.rooms.get_room(hotel_id=hotel_id, id=room_id)

        await self.db.commit()

        return room
