
from src.schemas.facilities import FacilityAdd


async def _create_facility(db):
    facility = await db.facilities.add(FacilityAdd(title="Test Facility"))
    await db.commit()
    return facility.id

async def _create_room_and_get_id(ac, db, title: str, **kwargs):
    facility_id = await _create_facility(db)
    await ac.post(
        "/hotels/1/rooms",
        json={
            "title": title,
            "description": "test",
            "price": 1000,
            "quantity": 1,
            "facilities_ids": [facility_id],
            **kwargs,
        },
    )
    rooms_resp = await ac.get(
        "/hotels/1/rooms",
        params={"date_from": "2026-01-01", "date_to": "2026-12-31"},
    )
    rooms = rooms_resp.json()
    for r in rooms:
        if r["title"] == title:
            return r["id"]
    raise AssertionError(f"Room with title '{title}' not found after creation")


async def test_get_rooms(ac):
    response = await ac.get(
        "/hotels/1/rooms",
        params={
            "date_from": "2026-06-01",
            "date_to": "2026-06-10",
        },
    )
    assert response.status_code == 200
    rooms = response.json()
    assert isinstance(rooms, list)
    assert len(rooms) > 0


async def test_get_rooms_not_found(ac):
    response = await ac.get(
        "/hotels/99999/rooms",
        params={
            "date_from": "2026-06-01",
            "date_to": "2026-06-10",
        },
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_create_room(ac, db):
    facility_id = await _create_facility(db)
    response = await ac.post(
        "/hotels/1/rooms",
        json={
            "title": "Test Room",
            "description": "A test room",
            "price": 5000,
            "quantity": 3,
            "facilities_ids": [facility_id],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"


async def test_create_room_invalid_hotel(ac, db):
    facility_id = await _create_facility(db)
    response = await ac.post(
        "/hotels/99999/rooms",
        json={
            "title": "Invalid Room",
            "description": None,
            "price": 1000,
            "quantity": 1,
            "facilities_ids": [facility_id],
        },
    )
    assert response.status_code == 404


async def test_get_room_by_id(ac):
    rooms_resp = await ac.get(
        "/hotels/1/rooms",
        params={"date_from": "2026-06-01", "date_to": "2026-06-10"},
    )
    assert rooms_resp.status_code == 200
    rooms = rooms_resp.json()
    assert len(rooms) > 0
    room_id = rooms[0]["id"]

    response = await ac.get(f"/hotels/1/rooms/{room_id}")
    assert response.status_code == 200
    room = response.json()
    assert room["id"] == room_id
    assert "facilities" in room


async def test_get_room_not_found(ac):
    response = await ac.get("/hotels/1/rooms/99999")
    assert response.status_code == 404


async def test_edit_room(ac, db):
    room_id = await _create_room_and_get_id(ac, db, "Editable Room", price=3000, quantity=2)
    facility_id = await _create_facility(db)

    put_resp = await ac.put(
        f"/hotels/1/rooms/{room_id}",
        json={
            "title": "Edited Room",
            "description": "After edit",
            "price": 4000,
            "quantity": 1,
            "facilities_ids": [facility_id],
        },
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["status"] == "OK"


async def test_patch_room(ac, db):
    room_id = await _create_room_and_get_id(ac, db, "Patchable Room", price=5000, quantity=2)

    patch_resp = await ac.patch(
        f"/hotels/1/rooms/{room_id}",
        json={"price": 9999},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "ok"


async def test_delete_room(ac, db):
    room_id = await _create_room_and_get_id(ac, db, "Deletable Room", price=2000, quantity=1)

    patch_resp = await ac.patch(f"/hotels/1/rooms/{room_id}", json={"facilities_ids": []})
    assert patch_resp.status_code == 200

    del_resp = await ac.delete(f"/hotels/1/rooms/{room_id}")
    assert del_resp.status_code == 200

    get_resp = await ac.get(f"/hotels/1/rooms/{room_id}")
    assert get_resp.status_code == 404
