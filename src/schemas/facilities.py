from pydantic import BaseModel, Field, ConfigDict

class FacilitiesAdd(BaseModel):
    title: str

class Facilities(FacilitiesAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomFacilitiesCreate(BaseModel):
    room_id: int
    facilities_id: int

class RoomFacility(RoomFacilitiesCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)