from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import DataError, IntegrityError

from src.exceptions import NotFoundError
from src.repositories.errors import translate_database_error
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def _execute(self, statement):
        try:
            return await self.session.execute(statement)
        except (IntegrityError, DataError) as exc:
            error = translate_database_error(exc)
            if error is not None:
                raise error from exc
            raise

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self._execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_by_id(self, id: int):
        query = select(self.model).filter_by(id=id)
        result = await self._execute(query)
        model = result.scalars().first()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self._execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filtered):
        query = select(self.model).filter_by(**filtered)
        result = await self._execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None

        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        stmt = await self._execute(add_data_stmt)
        model = stmt.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]):
        if not data:
            return
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self._execute(add_data_stmt)

    async def update(self, data: BaseModel, exclude_unset, **filter_by):
        update_data = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        result = await self._execute(update_data)
        model = result.scalars().one_or_none()
        if model is None:
            raise NotFoundError("Объект не найден")
        return model

    async def delete(self, **filter) -> BaseModel:
        delete_hotel = delete(self.model).filter_by(**filter).returning(self.model)
        stmt = await self._execute(delete_hotel)
        model = stmt.scalars().one_or_none()
        if model is None:
            raise NotFoundError("Объект не найден")
        return self.mapper.map_to_domain_entity(model)

    async def delete_all(self):
        query = delete(self.model)

        await self._execute(query)
