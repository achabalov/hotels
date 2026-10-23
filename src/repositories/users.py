from pydantic import EmailStr
from sqlalchemy import select

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import UserDataMapper
from src.schemas.users import UserWithHashedPassword


class UserRepository(BaseRepository):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr) -> UserWithHashedPassword | None:
        query = select(self.model).filter_by(email=email)
        result = await self._execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return UserWithHashedPassword.model_validate(model)
