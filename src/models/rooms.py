import typing

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, MappedColumn, relationship

from src.database import Base

if typing.TYPE_CHECKING:
    from src.models import FacilitiesOrm


class RoomsOrm(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = MappedColumn(primary_key=True)
    hotel_id: Mapped[int] = MappedColumn(ForeignKey('hotels.id'))
    title: Mapped[str] = MappedColumn(String(length=255))
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]

    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        back_populates='rooms',
        secondary='room_facilities',
    )
