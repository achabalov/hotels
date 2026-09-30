from datetime import date

from fastapi import Query, APIRouter, Body

from src.api.dependencies import PaginationDep, DBDep
from src.schemas.hotels import HotelAdd, HotelPatch

router = APIRouter(prefix='/hotels', tags=['отели'])


@router.get("/", summary='Получить все отели')
async def get_hotels(
        pagination: PaginationDep,
        db: DBDep,
        date_from: date,
        date_to: date,
        location: str | None = None,
        title: str | None = None
):
    per_page = pagination.per_page or 5
# return await db.hotels.get_all(
#     location=location,
#     title=title,
#     limit=pagination.per_page or 5,
#     offset=(pagination.page - 1) * per_page
# )
    return await db.hotels.get_filtered_by_date(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=pagination.per_page or 5,
        offset=(pagination.page - 1) * per_page
)


@router.get('/{hotel_id}', summary='Получить отель')
async def get_hotel_by_id(db: DBDep, hotel_id: int):
    return await db.hotels.get_one_or_none(id=hotel_id)


@router.post("", summary="Создать новый отель")
async def create_hotel(db: DBDep, hotel_data: HotelAdd = Body(openapi_examples={
    "1": {"summary": "Sochi", "value": {
        "title": "Отель Сочи 5 звезд",
        "location": "hotel sochi"
    }},
    "2": {"summary": "Dubai", "value": {
        "title": "Dubai",
        "location": "Dubai"
    }}
})):
    get_data_stmt = await db.hotels.add(hotel_data)
    await db.session.commit()

    return {"success": "ok", "data": get_data_stmt}


@router.put("/{hotel_id}", summary='Полное обновление данных об отеле')
async def put_hotel(db: DBDep, hotel_id: int, hotel_data: HotelAdd):
    await db.hotels.update(hotel_data, exclude_unset=False, id=hotel_id)
    await db.session.commit()

    return {"success": "ok"}


@router.patch("/{hotel_id}", summary='Частичное изменение данных об отеле')
async def update_hotel(db: DBDep, hotel_id: int, hotel_data: HotelPatch):
    await db.hotels.update(hotel_data, exclude_unset=True, id=hotel_id)
    await db.session.commit()

    return {"success": "ok"}


@router.delete("/{hotel_id}", summary='Удалить отель')
async def delete_hotel(db: DBDep, hotel_id: int):
    result = await db.hotels.delete(id=hotel_id)
    await db.session.commit()
    return {"status": "success", "data": result}
