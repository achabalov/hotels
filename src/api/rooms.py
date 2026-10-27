from datetime import date

from fastapi import APIRouter

from src.api.dependencies import DBDep, PositiveId
from src.schemas.rooms import RoomCreate, RoomResponse, RoomsPatch, RoomsWithRels
from src.services.rooms import RoomsService

router = APIRouter(prefix="/hotel", tags=["Комнаты"])


@router.get("/{hotel_id}/rooms/{room_id}", response_model=RoomsWithRels)
async def get_room(db: DBDep, hotel_id: PositiveId, room_id: PositiveId) -> RoomsWithRels:
    room = await RoomsService(db).get_room(hotel_id=hotel_id, room_id=room_id)
    return room

@router.get("/{hotel_id}/rooms")
async def get_rooms(db: DBDep, hotel_id: PositiveId, date_from: date, date_to: date):
    rooms = await RoomsService(db).get_rooms(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
    return rooms

@router.get("/all_rooms", response_model=list[RoomsWithRels])
async def get_all_rooms(db: DBDep) -> list[RoomsWithRels]:
    rooms = await RoomsService(db).get_all_rooms()
    return rooms

@router.post("/{hotel_id}/rooms")
async def create_room(db: DBDep, hotel_id: PositiveId, data: RoomCreate):
    room = await RoomsService(db).create_room(hotel_id=hotel_id, data=data)
    return room

@router.delete("/{hotel_id}/room/{room_id}", response_model=RoomResponse)
async def delete_room(db: DBDep, hotel_id: PositiveId, room_id: PositiveId):
    room = await RoomsService(db).delete_room(hotel_id=hotel_id, room_id=room_id)
    return room

@router.put("/{hotel_id}/room/{room_id}", response_model=RoomResponse)
async def put_room(db: DBDep, data: RoomCreate, hotel_id: PositiveId, room_id: PositiveId):
    room = await RoomsService(db).update_room(hotel_id=hotel_id, room_id=room_id, data=data)
    return room

@router.patch("/{hotel_id}/room/{room_id}", response_model=RoomResponse)
async def update_room(db: DBDep, data: RoomsPatch, hotel_id: PositiveId, room_id: PositiveId):
    room = await RoomsService(db).partial_update_room(hotel_id=hotel_id, room_id=room_id, data=data)
    return room