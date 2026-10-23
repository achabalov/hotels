from sqlalchemy.exc import DataError, IntegrityError

from src.repositories.bookings import BookingRepository
from src.repositories.errors import translate_database_error
from src.repositories.facilities import FacilitiesRepository, RoomsFacilitiesRepository
from src.repositories.hotels import HotelRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.users import UserRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.hotels = HotelRepository(self.session)
        self.users = UserRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.bookings = BookingRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.rooms_facilities = RoomsFacilitiesRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.session.rollback()
        finally:
            await self.session.close()

    async def commit(self):
        try:
            await self.session.commit()
        except (IntegrityError, DataError) as exc:
            error = translate_database_error(exc)
            if error is not None:
                raise error from exc
            raise
