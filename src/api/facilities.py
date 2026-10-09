from datetime import time

from fastapi import APIRouter
from functools import wraps
from src.api.dependencies import DBDep, cached, cache_clear
from src.schemas.facilities import Facilities, FacilitiesCreate

router = APIRouter(prefix='/facilities', tags=['facilities'])


@router.get('/', dependencies=[cached(ttl=60, group='facilities')])
async def get_all_facilities(db: DBDep):
    data = await db.facilities.get_all()

    return [Facilities.model_validate(item) for item in data]

@router.get('/{facility_id}', dependencies=[cached(ttl=60, group='facilities')])
async def get_facility(facility_id: int, db: DBDep):
    data = await db.facilities.get(facility_id)

    return Facilities.model_validate(data)

@router.post('/', dependencies=[cache_clear(group='facilities')])
async def create_facility(db: DBDep, data: FacilitiesCreate):
    data = await db.facilities.create(data.title)
    await db.session.commit()

    return Facilities.model_validate(data)






