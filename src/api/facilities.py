from fastapi import APIRouter

from src.api.dependencies import DBDep

router = APIRouter(prefix='/facilities', tags=['facilities'])


@router.get('/')
async def get_all_facilities(db: DBDep):
    data = await db.facilities.get_all()

    return data


@router.post('/create')
async def create_facility(db: DBDep, title: str):
    data = await db.facilities.create(title)
    await db.session.commit()

    return {'status': 'success', 'data': data}

