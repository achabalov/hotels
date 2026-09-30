from datetime import date

from src.repositories.base import BaseModel


class Bookings(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int

class BookingsCreate(BaseModel):
    room_id: int
    date_from: date
    date_to: date

class BookingsResponse(BaseModel):
    status: str
    data: Bookings