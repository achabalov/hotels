from sqlalchemy import select, insert, update, delete
from pydantic import BaseModel


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filtered):
        query = select(self.model).filter_by(**filtered)
        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None

        return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        stmt = await self.session.execute(add_data_stmt)
        model = stmt.scalars().one()
        return self.schema.model_validate(model, from_attributes=True)

    async def add_bulk(self, data: list[BaseModel]):
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def update(self, data: BaseModel, exclude_unset, **filter_by) -> None:
        update_data = update(self.model).filter_by(**filter_by).values(**data.model_dump(exclude_unset=exclude_unset))
        await self.session.execute(update_data)

    async def delete(self, **filter) -> BaseModel:
        delete_hotel = delete(self.model).filter_by(**filter).returning(self.model)
        stmt = await self.session.execute(delete_hotel)
        return self.schema.model_validate(stmt.scalars().one(), from_attributes=True)