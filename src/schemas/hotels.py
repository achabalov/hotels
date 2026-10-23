from pydantic import BaseModel, Field

from src.schemas.validation import NonEmptyString, PatchModel


class HotelAdd(BaseModel):
    title: NonEmptyString = Field(max_length=100)
    location: NonEmptyString


class Hotel(HotelAdd):
    id: int


class HotelPatch(PatchModel):
    title: NonEmptyString | None = Field(None, max_length=100)
    location: NonEmptyString | None = Field(None)
