from datetime import date

from src.schemas.bookings import BookingsAdd, BookingsCreate


async def test_add_booking(db):
    user = await db.users.get_by_id(1)
    room = await db.rooms.get_by_id(1)

    booking_data = BookingsAdd(
        room_id=room.id,
        user_id=user.id,
        date_from=date(2027, 1, 1),
        date_to=date(2027, 1, 9),
        price=200,
    )

    booking = await db.bookings.add_bookings(booking_data)

    await db.commit()

    assert booking.id is not None
    assert booking.user_id == user.id
    assert booking.room_id == room.id
    assert booking.price == 200
