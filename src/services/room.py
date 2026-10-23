from src.api.dependencies import DBDep
from src.exceptions import NotFoundError
from src.schemas.facilities import RoomFacilitiesCreate


class RoomService:
    @staticmethod
    async def validate_facilities(db: DBDep, facility_ids: list[int]):
        for facility_id in set(facility_ids):
            if await db.facilities.get_one_or_none(id=facility_id) is None:
                raise NotFoundError(f"Удобство {facility_id} не найдено")

    @staticmethod
    async def sync_facilities(db: DBDep, room_id: int, new_facility_ids: list[int]):
        await RoomService.validate_facilities(db, new_facility_ids)
        current_facility_ids = set(await db.rooms_facilities.get_room_facilities(room_id))
        new_facility_ids = set(new_facility_ids)
        facility_ids_to_add = new_facility_ids - current_facility_ids
        facility_ids_to_delete = current_facility_ids - new_facility_ids
        if facility_ids_to_delete:
            await db.rooms_facilities.delete_room_facilities(
                room_id=room_id, delete_facilities_ids=facility_ids_to_delete
            )

        if facility_ids_to_add:
            facilities_to_add = [
                RoomFacilitiesCreate(room_id=room_id, facilities_id=f_id)
                for f_id in facility_ids_to_add
            ]
            await db.rooms_facilities.add_bulk(facilities_to_add)
