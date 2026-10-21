import pytest


@pytest.mark.parametrize('room_id, date_from, date_to, status_code', [
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 200),
    (1, "2027-01-01", "2027-01-08", 500)
])
async def test_add_booking(room_id, date_from, date_to, status_code, db, authenticated_ac):
    # room = await db.rooms.get_by_id(1)
    response = await authenticated_ac.post('/bookings', json={
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to
    })

    assert response.status_code == status_code


@pytest.fixture(scope='module')
async def delete_all_bookings(db):
    await db.bookings.delete_all()
    await db.commit()

