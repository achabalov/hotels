from datetime import date

from fastapi import APIRouter, Body

from src.api.dependencies import DBDep, PaginationDep, PositiveId
from src.exceptions import NotFoundError
from src.schemas.hotels import HotelAdd, HotelPatch
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels", tags=["отели"])


@router.get("", summary="Получить все отели")
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    date_from: date,
    date_to: date,
    location: str | None = None,
    title: str | None = None,
):
    return await HotelService(db).get_filtered_by_date(
        date_from=date_from, date_to=date_to, pagination=pagination, location=location, title=title
    )


@router.get("/{hotel_id}", summary="Получить отель")
async def get_hotel_by_id(db: DBDep, hotel_id: PositiveId):
    hotel = await HotelService(db).get_hotel(hotel_id)
    if hotel is None:
        raise NotFoundError("Отель не найден")
    return hotel


@router.post("", summary="Создать новый отель")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(  # noqa: B008
        openapi_examples={
            "1": {
                "summary": "Sochi",
                "value": {"title": "Отель Сочи 5 звезд", "location": "hotel sochi"},
            },
            "2": {"summary": "Dubai", "value": {"title": "Dubai", "location": "Dubai"}},
        }
    ),
):
    hotel = await HotelService(db).create_hotel(hotel_data)
    return {"success": "ok", "data": hotel}


@router.put("/{hotel_id}", summary="Полное обновление данных об отеле")
async def put_hotel(db: DBDep, hotel_id: PositiveId, hotel_data: HotelAdd):
    await HotelService(db).update_hotel(hotel_id=hotel_id, data=hotel_data, exclude_unset=False)

    return {"success": "ok"}


@router.patch("/{hotel_id}", summary="Частичное изменение данных об отеле")
async def update_hotel(db: DBDep, hotel_id: PositiveId, hotel_data: HotelPatch):
    await HotelService(db).update_hotel(hotel_id=hotel_id, data=hotel_data, exclude_unset=True)

    return {"success": "ok"}


@router.delete("/{hotel_id}", summary="Удалить отель")
async def delete_hotel(db: DBDep, hotel_id: PositiveId):
    await HotelService(db).delete_hotel(hotel_id)
    return {"success": "ok"}
