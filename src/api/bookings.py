from fastapi import APIRouter
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest
from src.exceptions import (
    RoomNotFoundHTTPException,
    HotelNotFoundHTTPException,
    AllRoomsAreBookedHTTPException,
    RoomNotFoundException,
    HotelNotFoundException,
    AllRoomsAreBookedException,
    BookingNotFoundException,
)
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
async def get_bookings(db: DBDep):
    return await BookingService(db).get_bookings()


@router.get("/me")
async def get_user_bookings(user_id: UserIdDep, db: DBDep):
    return await BookingService(db).get_user_bookings(user_id)


@router.post("")
async def add_booking(user_id: UserIdDep, db: DBDep, booking_data: BookingAddRequest):
    try:
        booking = await BookingService(db).add_booking(user_id, booking_data)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except AllRoomsAreBookedException:
        raise AllRoomsAreBookedHTTPException
    return {"status": "OK", "data": booking}


@router.delete("/{booking_id}")
async def cancel_booking(user_id: UserIdDep, booking_id: int, db: DBDep):
    try:
        await BookingService(db).cancel_booking(user_id, booking_id)
    except BookingNotFoundException:
        raise BookingNotFoundException
    return {"status": "OK"}
