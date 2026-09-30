from pydantic import BaseModel, Field

class Rooms(BaseModel):
    title: str

class RoomsPatch(BaseModel):
    hotel_id: int = Field(None, alias="hotel_id")
    title: str | None = Field(None, alias="title")
    description: str | None = Field(None, alias="description")
    price: int | None = Field(None, alias="price")
    quantity: int | None = Field(None, alias="quantity")
    facilities_ids: list[int] | None = Field(None, alias="facilities_ids")

class RoomCreate(BaseModel):
    title: str
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
    facilities_ids: list[int] | None = None

class RoomResponse(BaseModel):
    id: int
    hotel_id: int
    title: str
    description: str | None = None
    price: int | None = None
    quantity: int | None = None

class RoomResponseStatus(BaseModel):
    status: str
    data: RoomResponse