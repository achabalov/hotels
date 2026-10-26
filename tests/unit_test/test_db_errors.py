import unittest
from unittest.mock import AsyncMock, Mock

from src.repositories.base import BaseRepository
from src.utils.db_manager import DBManager


class DatabaseCleanupTest(unittest.IsolatedAsyncioTestCase):
    async def test_error_rolls_back_and_closes_session(self):
        session = Mock(rollback=AsyncMock(), close=AsyncMock())
        with self.assertRaisesRegex(ValueError, 'failed request'):
            async with DBManager(session_factory=lambda: session):
                raise ValueError('failed request')
        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()

    async def test_session_closes_even_when_rollback_fails(self):
        session = Mock(rollback=AsyncMock(side_effect=ConnectionError()), close=AsyncMock())
        with self.assertRaises(ConnectionError):
            async with DBManager(session_factory=lambda: session):
                pass
        session.close.assert_awaited_once()

    async def test_empty_bulk_does_not_execute_insert(self):
        session = Mock(execute=AsyncMock())
        await BaseRepository(session).add_bulk([])
        session.execute.assert_not_awaited()


class RepositoryErrorsTest(unittest.IsolatedAsyncioTestCase):
    async def test_duplicate_is_domain_conflict(self):
        from sqlalchemy.exc import IntegrityError
        from src.exceptions import ConflictError
        from src.models.hotels import HotelsOrm
        from src.schemas.hotels import HotelAdd

        original = Exception('private SQL')
        original.sqlstate = '23505'
        session = Mock(execute=AsyncMock(side_effect=IntegrityError('SQL', {}, original)))
        repository = BaseRepository(session)
        repository.model = HotelsOrm
        with self.assertRaises(ConflictError):
            await repository.add(HotelAdd(title='Hotel', location='City'))

    async def test_deferred_constraint_at_commit(self):
        from sqlalchemy.exc import IntegrityError
        from src.exceptions import ConflictError

        original = Exception('private SQL')
        original.sqlstate = '23503'
        manager = DBManager(None)
        manager.session = Mock(commit=AsyncMock(side_effect=IntegrityError('SQL', {}, original)))
        with self.assertRaises(ConflictError):
            await manager.commit()

    async def test_invalid_booking_dates_do_not_access_database(self):
        from datetime import date
        from src.exceptions import InvalidDataError
        from src.repositories.bookings import BookingRepository
        from src.schemas.bookings import BookingsAdd

        session = Mock(execute=AsyncMock())
        with self.assertRaises(InvalidDataError):
            await BookingRepository(session).add_bookings(BookingsAdd(
                room_id=1, user_id=1, date_from=date(2027, 1, 3),
                date_to=date(2027, 1, 2), price=100))
        session.execute.assert_not_awaited()


class BookingOverlapTest(unittest.TestCase):
    def test_partial_full_and_touching_intervals(self):
        import sqlite3
        from datetime import date
        from sqlalchemy.dialects import sqlite
        from src.repositories.ustils import get_ids_for_booking

        with sqlite3.connect(':memory:') as connection:
            connection.execute('CREATE TABLE rooms (id INTEGER, hotel_id INTEGER, quantity INTEGER)')
            connection.execute('CREATE TABLE bookings (room_id INTEGER, date_from DATE, date_to DATE)')
            connection.execute('INSERT INTO rooms VALUES (1, 1, 1)')
            connection.execute("INSERT INTO bookings VALUES (1, '2027-01-10', '2027-01-15')")
            for start, end, available in [(8, 12, False), (12, 17, False),
                                           (8, 17, False), (11, 14, False),
                                           (5, 10, True), (15, 20, True)]:
                with self.subTest(start=start, end=end):
                    query = get_ids_for_booking(date(2027, 1, start), date(2027, 1, end))
                    sql = str(query.compile(dialect=sqlite.dialect(),
                                            compile_kwargs={'literal_binds': True}))
                    self.assertEqual(bool(connection.execute(sql).fetchall()), available)
