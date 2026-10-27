"""Изолированные проверки HTTP: python -m unittest tests.unit_test.test_api_errors."""

import importlib
import io
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from PIL import Image

from src.api.dependencies import get_current_user_id, get_db
from src.api.exception_handlers import register_exception_handlers
from src.config import settings
from src.exceptions import ConflictError, NotFoundError

# Эти тесты проверяют API без сетевых подключений и без lifespan приложения.
with (
    patch("src.api.dependencies.cached", lambda **kw: Depends(lambda: None)),
    patch("src.api.dependencies.cache_clear", lambda **kw: Depends(lambda: None)),
):
    routers = [
        importlib.import_module(f"src.api.{name}")
        for name in ("auth", "hotels", "rooms", "bookings", "facilities", "images")
    ]


class ApiErrorsTest(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        register_exception_handlers(self.app)
        for module in routers:
            self.app.include_router(module.router)
        self.db = SimpleNamespace(
            **{
                name: SimpleNamespace(
                    **{
                        method: AsyncMock(return_value=None)
                        for method in (
                            "get_one_or_none",
                            "get_room",
                            "get",
                            "update",
                            "delete",
                            "delete_room",
                            "get_user_with_hashed_password",
                            "add",
                            "create_room",
                            "add_bookings",
                            "add_bulk",
                            "get_filtered_by_date",
                        )
                    }
                )
                for name in (
                    "users",
                    "hotels",
                    "rooms",
                    "facilities",
                    "bookings",
                    "rooms_facilities",
                )
            }
        )
        self.db.session = SimpleNamespace(commit=AsyncMock())
        self.db.commit = self.db.session.commit
        self.db.users.get_one_or_none.return_value = SimpleNamespace(id=1)
        self.app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_unknown_login(self):
        response = self.client.post("/auth/login", json={"email": "a@example.com", "password": "x"})
        self.assertEqual(response.status_code, 401)

    def test_wrong_password(self):
        self.db.users.get_user_with_hashed_password.return_value = SimpleNamespace(
            id=1, hashed_password="hash"
        )
        with patch("src.api.auth.AuthService.verify_password", return_value=False):
            response = self.client.post(
                "/auth/login", json={"email": "a@example.com", "password": "x"}
            )
        self.assertEqual(response.status_code, 401)

    def test_missing_token(self):
        for url in ("/auth/me", "/bookings/me"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 401)

    def test_invalid_tokens(self):
        payloads = [
            {},
            {"user_id": True},
            {"user_id": "1"},
            {"user_id": -1},
            {"user_id": 1, "exp": datetime.now(UTC) - timedelta(seconds=1)},
        ]
        tokens = ["invalid"] + [
            jwt.encode(p, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
            for p in payloads
        ]
        for token in tokens:
            with self.subTest(token=token):
                self.client.cookies.set("access_token", token)
                self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_deleted_user(self):
        self.db.users.get_one_or_none.return_value = None
        self.app.dependency_overrides[get_current_user_id] = lambda: 1
        self.assertEqual(self.client.get("/auth/me").status_code, 401)

    def test_deleted_user_cannot_create_booking(self):
        self.app.dependency_overrides[get_current_user_id] = lambda: 1
        self.db.users.get_one_or_none.return_value = None
        response = self.client.post(
            "/bookings", json={"room_id": 1, "date_from": "2027-01-01", "date_to": "2027-01-02"}
        )
        self.assertEqual(response.status_code, 401)
        self.db.bookings.add_bookings.assert_not_awaited()
        self.db.commit.assert_not_awaited()

    def test_missing_resources(self):
        self.db.facilities.get.side_effect = NotFoundError("Удобство не найдено")
        self.db.hotels.delete.side_effect = NotFoundError("Объект не найден")
        requests = [
            ("GET", "/hotels/1", None),
            ("DELETE", "/hotels/1", None),
            ("GET", "/hotel/1/rooms/1", None),
            ("DELETE", "/hotel/1/room/1", None),
            ("PATCH", "/hotel/1/room/1", {"title": "test"}),
            ("PUT", "/hotel/1/room/1", {"title": "test", "price": 1, "quantity": 1}),
            ("GET", "/facilities/1", None),
        ]
        for method, url, body in requests:
            with self.subTest(method=method, url=url):
                self.assertEqual(self.client.request(method, url, json=body).status_code, 404)
        self.db.session.commit.assert_not_awaited()

    def test_missing_hotel_for_rooms(self):
        response = self.client.get(
            "/hotel/1/rooms", params={"date_from": "2027-01-01", "date_to": "2027-01-02"}
        )
        self.assertEqual(response.status_code, 404)
        response = self.client.post(
            "/hotel/1/rooms", json={"title": "Room", "price": 100, "quantity": 1}
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_facility_for_room(self):
        self.db.hotels.get_one_or_none.return_value = SimpleNamespace(id=1)
        response = self.client.post(
            "/hotel/1/rooms",
            json={"title": "Room", "price": 100, "quantity": 1, "facilities_ids": [99]},
        )
        self.assertEqual(response.status_code, 404)
        self.db.rooms.create_room.assert_not_awaited()

    def test_empty_and_null_patches(self):
        for url in ("/hotels/1", "/hotel/1/room/1"):
            for body in ({}, {"title": None}, {"title": "   "}):
                with self.subTest(url=url, body=body):
                    self.assertEqual(self.client.patch(url, json=body).status_code, 422)

    def test_invalid_creation_data(self):
        cases = [
            ("/hotels", {"title": "", "location": "test"}),
            ("/facilities", {"title": " "}),
            ("/hotel/1/rooms", {"title": "R", "price": -1, "quantity": 1}),
            ("/hotel/1/rooms", {"title": "R", "price": 1, "quantity": 0}),
            ("/hotel/1/rooms", {"title": "R"}),
            ("/auth/register", {"email": "a@example.com", "password": ""}),
        ]
        for url, body in cases:
            with self.subTest(url=url, body=body):
                self.assertEqual(self.client.post(url, json=body).status_code, 422)

    def test_invalid_path_ids(self):
        for url in ("/hotels/0", "/facilities/-1", "/hotel/1/rooms/0"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 422)

    def test_booking_errors(self):
        self.app.dependency_overrides[get_current_user_id] = lambda: 1
        body = {"room_id": 1, "date_from": "2027-01-01", "date_to": "2027-01-02"}
        self.assertEqual(self.client.post("/bookings", json=body).status_code, 404)
        self.db.rooms.get_room.return_value = SimpleNamespace(price=100)
        self.db.bookings.add_bookings.side_effect = ConflictError("Номер занят")
        self.assertEqual(self.client.post("/bookings", json=body).status_code, 409)
        body["date_to"] = "2027-01-01"
        self.assertEqual(self.client.post("/bookings", json=body).status_code, 422)
        self.db.session.commit.assert_not_awaited()

    def test_invalid_search_dates(self):
        response = self.client.get(
            "/hotels", params={"date_from": "2027-01-02", "date_to": "2027-01-01"}
        )
        self.assertEqual(response.status_code, 422)

    def test_empty_room_facilities_do_not_insert(self):
        # Проверка успешного сценария без удобств — раньше INSERT пустого списка падал.
        self.db.hotels.get_one_or_none.return_value = SimpleNamespace(id=1)
        self.db.rooms.create_room.return_value = SimpleNamespace(id=1)
        self.assertEqual(
            self.client.post(
                "/hotel/1/rooms", json={"title": "Room", "price": 1, "quantity": 1}
            ).status_code,
            200,
        )

    def test_images(self):
        image = io.BytesIO()
        Image.new("RGB", (2, 2)).save(image, format="PNG")
        module = importlib.import_module("src.services.images")
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(module, "IMAGES_DIR", Path(directory)),
            patch.object(module, "resize_image") as resize,
        ):
            for data in (b"", b"not an image"):
                response = self.client.post("/images", files={"file": ("x.png", data)})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(list(Path(directory).iterdir()), [])
            response = self.client.post(
                "/images", files={"file": ("../../escape.png", image.getvalue())}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)
            self.assertNotIn("/", response.json()["filename"])
            resize.assert_called_once()

    def test_image_size_limits(self):
        module = importlib.import_module("src.services.images")
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(module, "IMAGES_DIR", Path(directory)),
            patch.object(module, "MAX_FILE_SIZE", 3),
        ):
            response = self.client.post("/images", files={"file": ("x.png", b"1234")})
            self.assertEqual(response.status_code, 413)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_missing_hotel_updates(self):
        self.db.hotels.update.side_effect = NotFoundError("Объект не найден")
        for method, body in [
            ("PUT", {"title": "test", "location": "test"}),
            ("PATCH", {"title": "test"}),
        ]:
            with self.subTest(method=method):
                self.assertEqual(
                    self.client.request(method, "/hotels/1", json=body).status_code, 404
                )
        self.db.session.commit.assert_not_awaited()

    def test_missing_facility_for_patch(self):
        self.db.rooms.get_room.return_value = SimpleNamespace(id=1)
        response = self.client.patch("/hotel/1/room/1", json={"facilities_ids": [99]})
        self.assertEqual(response.status_code, 404)
        self.db.rooms.update.assert_not_awaited()
        self.db.session.commit.assert_not_awaited()

    def test_room_put_requires_complete_data(self):
        response = self.client.put("/hotel/1/room/1", json={"title": "Room"})
        self.assertEqual(response.status_code, 422)

    def test_unsupported_image_format(self):
        data = io.BytesIO()
        Image.new("RGB", (1, 1)).save(data, format="BMP")
        module = importlib.import_module("src.services.images")
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(module, "IMAGES_DIR", Path(directory)),
        ):
            response = self.client.post("/images", files={"file": ("a.bmp", data.getvalue())})
            self.assertEqual(response.status_code, 415)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_image_storage_unavailable(self):
        with (
            patch("src.services.images.Path.mkdir", side_effect=PermissionError("private")),
            self.assertLogs("src.services.images", level="ERROR"),
        ):
            response = self.client.post("/images", files={"file": ("a.png", b"data")})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)

    def test_background_image_error_is_logged(self):
        module = importlib.import_module("src.services.images")
        with (
            patch.object(module, "resize_image", side_effect=ValueError("bad image")),
            self.assertLogs("src.services.images", level="ERROR"),
        ):
            module.resize_uploaded_image("test.png")
