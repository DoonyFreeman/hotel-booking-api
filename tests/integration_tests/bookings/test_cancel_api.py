import pytest
from src.exceptions import BookingNotFoundException

async def test_cancel_booking(authenticated_ac):
    create_resp = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": 1,
            "date_from": "2027-01-01",
            "date_to": "2027-01-05",
        },
    )
    assert create_resp.status_code == 200
    booking_id = create_resp.json()["data"]["id"]

    cancel_resp = await authenticated_ac.delete(f"/bookings/{booking_id}")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "OK"


async def test_cancel_nonexistent_booking(authenticated_ac):
    with pytest.raises(BookingNotFoundException):
        await authenticated_ac.delete("/bookings/99999")


async def test_get_all_bookings(authenticated_ac):
    response = await authenticated_ac.get("/bookings")
    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)


async def test_get_my_bookings(authenticated_ac):
    response = await authenticated_ac.get("/bookings/me")
    assert response.status_code == 200
    bookings = response.json()
    assert isinstance(bookings, list)
