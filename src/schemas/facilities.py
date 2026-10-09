from pydantic import BaseModel, ConfigDict

class FacilitiesCreate(BaseModel):
    title: str

class Facilities(FacilitiesCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomFacilitiesCreate(BaseModel):
    room_id: int
    facilities_id: int

class RoomFacility(RoomFacilitiesCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)