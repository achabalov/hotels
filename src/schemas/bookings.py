from datetime import date

from pydantic import BaseModel, Field


class BookingsCreate(BaseModel):
    room_id: int = Field(gt=0)
    date_from: date
    date_to: date


class BookingsAdd(BaseModel):
    room_id: int = Field(gt=0)
    user_id: int
    date_from: date
    date_to: date
    price: int


class BookingsAddRequest(BaseModel):
    room_id: int = Field(gt=0)
    date_from: date
    date_to: date


class Bookings(BaseModel):
    id: int
    room_id: int = Field(gt=0)
    user_id: int
    date_from: date
    date_to: date
    price: int
