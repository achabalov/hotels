from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, ForeignKey

from src.database import Base

class RoomsOrm(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = MappedColumn(primary_key=True)
    hotel_id: Mapped[int] = MappedColumn(ForeignKey('hotels.id'))
    title: Mapped[str] = MappedColumn(String(length=255))
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]
