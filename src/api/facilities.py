from fastapi import APIRouter

from src.api.dependencies import DBDep, PositiveId, cache_clear, cached
from src.schemas.facilities import FacilitiesCreate
from src.services.facilities import FacilitiesService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", dependencies=[cached(ttl=60, group="facilities")])
async def get_all_facilities(db: DBDep):
    facilities = await FacilitiesService(db).get_all_facilities()
    return facilities


@router.get("/{facility_id}", dependencies=[cached(ttl=60, group="facilities")])
async def get_facility(facility_id: PositiveId, db: DBDep):
    facility = await FacilitiesService(db).get_facility(facility_id)
    return facility

@router.post("", dependencies=[cache_clear(group="facilities")])
async def create_facility(db: DBDep, data: FacilitiesCreate):
    facility = await FacilitiesService(db).create_facility(title=data.title)
    return facility