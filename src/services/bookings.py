from src.services.base import BaseService
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.schemas.rooms import Room
from src.schemas.hotels import Hotel
from src.exceptions import (
    ObjectNotFoundException,
    RoomNotFoundException,
    HotelNotFoundException,
    AllRoomsAreBookedException,
    BookingNotFoundException,
)
from src.metrics import BOOKINGS_CREATED, BOOKINGS_CANCELLED


class BookingService(BaseService):
    async def get_bookings(self):
        return await self.db.bookings.get_all()

    async def get_user_bookings(self, user_id: int):
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def add_booking(self, user_id: int, booking_data: BookingAddRequest):
        try:
            room: Room = await self.db.rooms.get_one(id=booking_data.room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException

        try:
            hotel: Hotel = await self.db.hotels.get_one(id=room.hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException

        room_price: int = room.price
        _booking_data = BookingAdd(
            user_id=user_id,
            price=room_price,
            **booking_data.model_dump(),
        )
        try:
            booking = await self.db.bookings.add_booking(_booking_data, hotel_id=hotel.id)
        except AllRoomsAreBookedException:
            raise AllRoomsAreBookedException
        BOOKINGS_CREATED.labels(hotel_id=str(hotel.id)).inc()
        await self.db.commit()
        return booking

    async def cancel_booking(self, user_id: int, booking_id: int):
        cancelled = await self.db.bookings.cancel_booking(booking_id, user_id)
        if not cancelled:
            raise BookingNotFoundException
        BOOKINGS_CANCELLED.inc()
        await self.db.commit()
