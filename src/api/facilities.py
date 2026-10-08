import json

from fastapi import APIRouter

from src.api.dependencies import DBDep
from src.init import redis_manager
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import Facilities

router = APIRouter(prefix='/facilities', tags=['facilities'])


@router.get('/')
async def get_all_facilities(db: DBDep):
    redis_facilities = await redis_manager.get('facilities')
    if redis_facilities is None:
        data = await db.facilities.get_all()
        facilities = [FacilityDataMapper.map_to_domain_entity(item) for item in data]
        await redis_manager.set('facilities', json.dumps([item.model_dump() for item in facilities]), expire=60)
        return data

    return [Facilities.model_validate(item) for item in json.loads(redis_facilities)]

@router.get('/{facility_id}')
async def get_facility(facility_id: int, db: DBDep):
    data = await db.facilities.get(facility_id)

    return data

@router.post('/create')
async def create_facility(db: DBDep, title: str):
    data = await db.facilities.create(title)
    await db.session.commit()

    return {'status': 'success', 'data': data}

