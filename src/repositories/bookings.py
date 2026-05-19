from datetime import date
from sqlalchemy import select, update

from src.repositories.base import BaseRepository
from src.models import BookingsOrm
from src.schemas.bookings import BookingAdd
from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.utils import rooms_ids_for_booking

from src.exceptions import AllRoomsAreBookedException


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_booking(self, data: BookingAdd, hotel_id: int):
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
            hotel_id=hotel_id,
        )
        rooms_ids_to_book_res = await self.session.execute(rooms_ids_to_get)
        rooms_ids_to_book: list[int] = rooms_ids_to_book_res.scalars().all()  # type: ignore

        if data.room_id in rooms_ids_to_book:
            new_booking = await self.add(data)
            return new_booking

        raise AllRoomsAreBookedException

    async def cancel_booking(self, booking_id: int, user_id: int) -> bool:
        stmt = (
            update(BookingsOrm)
            .where(BookingsOrm.id == booking_id, BookingsOrm.user_id == user_id, BookingsOrm.is_cancelled.is_(False))
            .values(is_cancelled=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
