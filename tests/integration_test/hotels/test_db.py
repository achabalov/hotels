from src.schemas.hotels import HotelAdd


async def test_add_hotels(db):
    hotel_data = HotelAdd(title='Hotel 5 stars', location='San Francisco, CA')
    await db.hotels.add(hotel_data)
    await db.commit()