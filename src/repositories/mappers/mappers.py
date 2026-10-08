from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Bookings
from src.schemas.facilities import Facilities
from src.schemas.hotels import Hotel
from src.schemas.rooms import Rooms, RoomsWithRels
from src.schemas.users import User


class HotelDataMapper(DataMapper):
    schema = Hotel
    db_model = HotelsOrm

class RoomDataMapper(DataMapper):
    schema = Rooms
    db_model = RoomsOrm

class RoomDataWithRelsMapper(DataMapper):
    schema = RoomsWithRels
    db_model = RoomsOrm

class UserDataMapper(DataMapper):
    schema = User
    db_model = UsersOrm

class BookingDataMapper(DataMapper):
    schema = Bookings
    db_model = BookingsOrm

class FacilityDataMapper(DataMapper):
    schema = Facilities
    db_model = FacilitiesOrm
