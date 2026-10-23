from typing import Annotated

from pydantic import BaseModel, Field

from src.schemas.facilities import Facilities
from src.schemas.validation import NonEmptyString, PatchModel


class Rooms(BaseModel):
    id: int
    title: str


class RoomsPatch(PatchModel):
    title: NonEmptyString | None = Field(None, max_length=255)
    description: str | None = Field(None, alias="description")
    price: int | None = Field(None, ge=0)
    quantity: int | None = Field(None, ge=1)
    facilities_ids: list[Annotated[int, Field(gt=0)]] | None = None


class RoomCreate(BaseModel):
    title: NonEmptyString = Field(max_length=255)
    description: str | None = None
    price: int = Field(ge=0)
    quantity: int = Field(ge=1)
    facilities_ids: list[Annotated[int, Field(gt=0)]] = Field(default_factory=list)


class RoomResponse(BaseModel):
    id: int
    hotel_id: int
    title: str
    description: str | None = None
    price: int | None = None
    quantity: int | None = None


class RoomsWithRels(BaseModel):
    id: int
    hotel_id: int
    title: str
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
    facilities: list[Facilities]


class RoomSeed(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
