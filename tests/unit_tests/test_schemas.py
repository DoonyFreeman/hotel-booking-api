from datetime import date

import pytest
from pydantic import ValidationError

from src.schemas.hotels import HotelAdd, HotelPATCH
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest
from src.schemas.bookings import BookingAddRequest
from src.schemas.users import UserRequestAdd
from src.schemas.facilities import FacilityAdd


class TestHotelSchemas:
    def test_hotel_add_valid(self):
        data = HotelAdd(title="Test Hotel", location="Moscow")
        assert data.title == "Test Hotel"
        assert data.location == "Moscow"

    def test_hotel_add_missing_field(self):
        with pytest.raises(ValidationError):
            HotelAdd(title="Test Hotel")

    def test_hotel_patch_empty(self):
        data = HotelPATCH()
        assert data.title is None
        assert data.location is None

    def test_hotel_patch_partial(self):
        data = HotelPATCH(title="New Title")
        assert data.title == "New Title"
        assert data.location is None


class TestRoomSchemas:
    def test_room_add_request_valid(self):
        data = RoomAddRequest(
            title="Suite",
            description="Nice room",
            price=10000,
            quantity=2,
            facilities_ids=[1, 2],
        )
        assert data.title == "Suite"
        assert data.price == 10000
        assert data.facilities_ids == [1, 2]

    def test_room_add_request_default_facilities(self):
        data = RoomAddRequest(
            title="Suite",
            description="Nice room",
            price=10000,
            quantity=2,
        )
        assert data.facilities_ids == []

    def test_room_add_request_missing_required(self):
        with pytest.raises(ValidationError):
            RoomAddRequest(title="Suite", price=10000)

    def test_room_patch_request_empty(self):
        data = RoomPatchRequest()
        assert data.title is None
        assert data.price is None
        assert data.facilities_ids == []

    def test_room_patch_request_partial(self):
        data = RoomPatchRequest(price=15000)
        assert data.price == 15000
        assert data.title is None


class TestBookingSchemas:
    def test_booking_add_request_valid(self):
        data = BookingAddRequest(
            room_id=1,
            date_from=date(2026, 6, 1),
            date_to=date(2026, 6, 10),
        )
        assert data.room_id == 1
        assert data.date_from == date(2026, 6, 1)

    def test_booking_add_request_invalid_dates(self):
        with pytest.raises(ValidationError):
            BookingAddRequest(
                room_id=1,
                date_from="invalid-date",
                date_to=date(2026, 6, 10),
            )


class TestUserSchemas:
    def test_user_request_add_valid(self):
        data = UserRequestAdd(email="test@example.com", password="secret")
        assert data.email == "test@example.com"
        assert data.password == "secret"

    def test_user_request_add_invalid_email(self):
        with pytest.raises(ValidationError):
            UserRequestAdd(email="not-an-email", password="secret")


class TestFacilitySchemas:
    def test_facility_add_valid(self):
        data = FacilityAdd(title="Wi-Fi")
        assert data.title == "Wi-Fi"

    def test_facility_add_missing_title(self):
        with pytest.raises(ValidationError):
            FacilityAdd()
