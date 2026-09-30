from datetime import date

from fastapi import APIRouter

from src.api.dependencies import DBDep
from src.schemas.facilities import RoomFacilitiesAdd
from src.schemas.rooms import RoomResponse, RoomCreate, RoomResponseStatus, RoomsPatch

router = APIRouter(prefix="/hotel", tags=["rooms"])


@router.get('/{hotel_id}/rooms/{room_id}', response_model=RoomResponse)
async def get_room(db: DBDep, hotel_id: int, room_id: int) -> RoomResponse:
    data = await db.rooms.get_room(hotel_id=hotel_id, id=room_id)
    return data


@router.get('/{hotel_id}/rooms')
async def get_rooms(db: DBDep, hotel_id: int | None, date_from: date, date_to: date):
    rooms = await db.rooms.get_filtered_by_date(
        date_from=date_from,
        date_to=date_to,
        hotel_id=hotel_id
    )
    return rooms


@router.get('/all_rooms', response_model=list[RoomResponse])
async def get_all_rooms(db: DBDep) -> list[RoomResponse]:
    data = await db.rooms.get_all()
    return data


@router.post('/{hotel_id}/rooms')
async def create_room(db: DBDep, hotel_id: int, data: RoomCreate):
    facilities_ids = data.facilities_ids

    data = await db.rooms.create_room(data, hotel_id=hotel_id)

    rooms_facilities_data = [RoomFacilitiesAdd(room_id=data.id, facilities_id=f_id) for f_id in facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.session.commit()
    return data


@router.delete('/{hotel_id}/room/{room_id}', response_model=RoomResponseStatus)
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
    result = await db.rooms.delete_room(hotel_id=hotel_id, id=room_id)
    await db.session.commit()
    return {'status': 'ok', "data": result}


@router.put('/{hotel_id}/room/{room_id}', response_model=RoomResponseStatus)
async def put_room(db: DBDep, data: RoomsPatch, hotel_id: int, room_id: int):
    result = await db.rooms.update(data, exclude_unset=False, id=room_id, hotel_id=hotel_id)
    await db.session.commit()
    return {'status': 'ok', "data": result}


@router.patch('/{hotel_id}/room/{room_id}', response_model=RoomResponseStatus)
async def update_room(db: DBDep, data: RoomsPatch, hotel_id: int, room_id: int):
    result = await db.rooms.update(data, exclude_unset=True, hotel_id=hotel_id, id=room_id)
    await db.session.commit()
    return {'status': 'ok', "data": result}
