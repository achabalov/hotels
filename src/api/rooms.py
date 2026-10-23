from datetime import date

from fastapi import APIRouter

from src.api.dependencies import DBDep, PositiveId
from src.exceptions import NotFoundError, validate_dates
from src.repositories.mappers.mappers import RoomDataWithRelsMapper
from src.schemas.facilities import RoomFacilitiesCreate
from src.schemas.rooms import RoomCreate, RoomResponse, RoomsPatch, RoomsWithRels
from src.services.room import RoomService

router = APIRouter(prefix="/hotel", tags=["Комнаты"])


@router.get("/{hotel_id}/rooms/{room_id}", response_model=RoomsWithRels)
async def get_room(db: DBDep, hotel_id: PositiveId, room_id: PositiveId) -> RoomsWithRels:
    data = await db.rooms.get_room(hotel_id=hotel_id, id=room_id)

    if data is None:
        raise NotFoundError("Номер не найден")
    return RoomDataWithRelsMapper.map_to_domain_entity(data)


@router.get("/{hotel_id}/rooms")
async def get_rooms(db: DBDep, hotel_id: PositiveId, date_from: date, date_to: date):
    if await db.hotels.get_one_or_none(id=hotel_id) is None:
        raise NotFoundError("Отель не найден")
    validate_dates(date_from, date_to)
    rooms = await db.rooms.get_filtered_by_date(
        date_from=date_from, date_to=date_to, hotel_id=hotel_id
    )
    return rooms


@router.get("/all_rooms", response_model=list[RoomsWithRels])
async def get_all_rooms(db: DBDep) -> list[RoomsWithRels]:
    data = await db.rooms.get_all()
    return [RoomDataWithRelsMapper.map_to_domain_entity(room) for room in data]


@router.post("/{hotel_id}/rooms")
async def create_room(db: DBDep, hotel_id: PositiveId, data: RoomCreate):
    if await db.hotels.get_one_or_none(id=hotel_id) is None:
        raise NotFoundError("Отель не найден")
    facilities_ids = list(set(data.facilities_ids))
    await RoomService.validate_facilities(db, facilities_ids)

    data = await db.rooms.create_room(data, hotel_id=hotel_id)

    rooms_facilities_data = [
        RoomFacilitiesCreate(room_id=data.id, facilities_id=f_id) for f_id in facilities_ids
    ]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()
    return data


@router.delete("/{hotel_id}/room/{room_id}", response_model=RoomResponse)
async def delete_room(db: DBDep, hotel_id: PositiveId, room_id: PositiveId):
    result = await db.rooms.delete_room(hotel_id=hotel_id, id=room_id)
    if result is None:
        raise NotFoundError("Номер не найден")
    await db.commit()
    return result


@router.put("/{hotel_id}/room/{room_id}", response_model=RoomResponse)
async def put_room(db: DBDep, data: RoomCreate, hotel_id: PositiveId, room_id: PositiveId):
    if await db.rooms.get_room(hotel_id=hotel_id, id=room_id) is None:
        raise NotFoundError("Номер не найден")
    if data.facilities_ids is not None:
        await RoomService.sync_facilities(
            db=db,
            room_id=room_id,
            new_facility_ids=data.facilities_ids,
        )

    result = await db.rooms.update(
        data,
        exclude_unset=False,
        id=room_id,
        hotel_id=hotel_id,
    )

    await db.commit()

    return result


@router.patch("/{hotel_id}/room/{room_id}", response_model=RoomResponse)
async def update_room(db: DBDep, data: RoomsPatch, hotel_id: PositiveId, room_id: PositiveId):
    if await db.rooms.get_room(hotel_id=hotel_id, id=room_id) is None:
        raise NotFoundError("Номер не найден")
    if data.facilities_ids is not None:
        await RoomService.sync_facilities(
            db=db,
            room_id=room_id,
            new_facility_ids=data.facilities_ids,
        )
    update_data = data.model_dump(
        exclude_unset=True,
        exclude={"facilities_ids", "hotel_id"},
    )
    if update_data:
        await db.rooms.update(
            data,
            exclude_unset=True,
            id=room_id,
            hotel_id=hotel_id,
        )

    result = await db.rooms.get_room(hotel_id=hotel_id, id=room_id)

    await db.commit()

    return result
