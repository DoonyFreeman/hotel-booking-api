from src.schemas.rooms import RoomAdd


async def test_room_db_add_and_get(db):
    room_data = RoomAdd(
        hotel_id=1,
        title="DB Room",
        description="From DB test",
        price=7000,
        quantity=4,
    )
    room = await db.rooms.add(room_data)
    await db.commit()

    assert room.id is not None
    assert room.title == "DB Room"
    assert room.price == 7000

    fetched = await db.rooms.get_one(id=room.id, hotel_id=1)
    assert fetched.title == "DB Room"


async def test_room_db_edit(db):
    room_data = RoomAdd(
        hotel_id=1,
        title="Edit Room",
        description=None,
        price=8000,
        quantity=2,
    )
    room = await db.rooms.add(room_data)
    await db.commit()

    updated_data = RoomAdd(
        hotel_id=1,
        title="Edited Room",
        description="Updated",
        price=9000,
        quantity=3,
    )
    await db.rooms.edit(updated_data, id=room.id)
    await db.commit()

    fetched = await db.rooms.get_one(id=room.id, hotel_id=1)
    assert fetched.title == "Edited Room"
    assert fetched.price == 9000
    assert fetched.quantity == 3


async def test_room_db_delete(db):
    room_data = RoomAdd(
        hotel_id=1,
        title="Delete Room",
        description=None,
        price=5000,
        quantity=1,
    )
    room = await db.rooms.add(room_data)
    await db.commit()

    await db.rooms.delete(id=room.id, hotel_id=1)
    await db.commit()

    fetched = await db.rooms.get_one_or_none(id=room.id)
    assert fetched is None


async def test_room_db_get_filtered_by_hotel(db):
    rooms = await db.rooms.get_filtered(hotel_id=1)
    assert len(rooms) > 0
    for room in rooms:
        assert room.hotel_id == 1


async def test_room_db_get_all(db):
    all_rooms = await db.rooms.get_all()
    assert len(all_rooms) >= 4
