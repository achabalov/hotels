from pydantic import BaseModel, ConfigDict, Field

from src.schemas.validation import NonEmptyString


class FacilitiesCreate(BaseModel):
    title: NonEmptyString = Field(max_length=100)


class Facilities(FacilitiesCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomFacilitiesCreate(BaseModel):
    room_id: int
    facilities_id: int


class RoomFacility(RoomFacilitiesCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
