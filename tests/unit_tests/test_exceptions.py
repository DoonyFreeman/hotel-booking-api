import pytest

from src.exceptions import (
    NabronirovalException,
    ObjectNotFoundException,
    RoomNotFoundException,
    HotelNotFoundException,
    ObjectAlreadyExistsException,
    AllRoomsAreBookedException,
    BookingNotFoundException,
    IncorrectTokenException,
    EmailNotRegisteredException,
    IncorrectPasswordException,
    UserAlreadyExistsException,
    HotelNotFoundHTTPException,
    RoomNotFoundHTTPException,
    NoAccessTokenHTTPException,
    IncorrectTokenHTTPException,
    check_date_to_after_date_from,
)
from datetime import date
from fastapi import HTTPException


class TestDomainExceptions:
    def test_base_exception_default_message(self):
        with pytest.raises(NabronirovalException) as exc:
            raise NabronirovalException
        assert "Неожиданная ошибка" in str(exc.value)

    def test_object_not_found(self):
        with pytest.raises(ObjectNotFoundException) as exc:
            raise ObjectNotFoundException
        assert "Объект не найден" in str(exc.value)

    def test_room_not_found(self):
        with pytest.raises(RoomNotFoundException):
            raise RoomNotFoundException

    def test_hotel_not_found(self):
        with pytest.raises(HotelNotFoundException):
            raise HotelNotFoundException

    def test_object_already_exists(self):
        with pytest.raises(ObjectAlreadyExistsException):
            raise ObjectAlreadyExistsException

    def test_all_rooms_are_booked(self):
        with pytest.raises(AllRoomsAreBookedException):
            raise AllRoomsAreBookedException

    def test_booking_not_found(self):
        with pytest.raises(BookingNotFoundException):
            raise BookingNotFoundException

    def test_incorrect_token(self):
        with pytest.raises(IncorrectTokenException):
            raise IncorrectTokenException

    def test_email_not_registered(self):
        with pytest.raises(EmailNotRegisteredException):
            raise EmailNotRegisteredException

    def test_incorrect_password(self):
        with pytest.raises(IncorrectPasswordException):
            raise IncorrectPasswordException

    def test_user_already_exists(self):
        with pytest.raises(UserAlreadyExistsException):
            raise UserAlreadyExistsException


class TestHTTPExceptions:
    def test_hotel_not_found_http(self):
        with pytest.raises(HotelNotFoundHTTPException) as exc:
            raise HotelNotFoundHTTPException
        assert exc.value.status_code == 404
        assert exc.value.detail == "Отель не найден"

    def test_room_not_found_http(self):
        with pytest.raises(RoomNotFoundHTTPException) as exc:
            raise RoomNotFoundHTTPException
        assert exc.value.status_code == 404

    def test_no_access_token_http(self):
        with pytest.raises(NoAccessTokenHTTPException) as exc:
            raise NoAccessTokenHTTPException
        assert exc.value.status_code == 401

    def test_incorrect_token_http(self):
        with pytest.raises(IncorrectTokenHTTPException) as exc:
            raise IncorrectTokenHTTPException
        assert exc.value.status_code == 401


class TestCheckDate:
    def test_valid_dates(self):
        check_date_to_after_date_from(date(2026, 6, 1), date(2026, 6, 10))

    def test_equal_dates(self):
        with pytest.raises(HTTPException) as exc:
            check_date_to_after_date_from(date(2026, 6, 10), date(2026, 6, 10))
        assert exc.value.status_code == 422

    def test_date_to_before_date_from(self):
        with pytest.raises(HTTPException) as exc:
            check_date_to_after_date_from(date(2026, 6, 10), date(2026, 6, 1))
        assert exc.value.status_code == 422
