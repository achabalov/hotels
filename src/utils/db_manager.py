from src.repositories.hotels import HotelRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.bookings import BookingRepository
from src.repositories.users import UserRepository
from src.repositories.facilities import FacilitiesRepository, RoomsFacilitiesRepository


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
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()