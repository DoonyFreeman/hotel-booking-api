from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date
from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Boolean


class BookingsOrm(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    date_from: Mapped[date]
    date_to: Mapped[date]
    price: Mapped[int]
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    @hybrid_property
    def total_cost(self) -> int:
        days = (self.date_to - self.date_from).days
        return days * self.price
