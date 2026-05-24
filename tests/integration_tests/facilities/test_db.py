from src.schemas.facilities import FacilityAdd
from src.schemas.rooms import RoomAdd
from src.repositories.facilities import RoomsFacilitiesRepository


async def test_facility_db_add_and_get(db):
    facility_data = FacilityAdd(title="Sauna")
    facility = await db.facilities.add(facility_data)
    await db.commit()

    assert facility.id is not None
    assert facility.title == "Sauna"

    fetched = await db.facilities.get_one(id=facility.id)
    assert fetched.title == "Sauna"


async def test_facility_db_get_all(db):
    all_facilities = await db.facilities.get_all()
    assert isinstance(all_facilities, list)


async def test_facility_db_delete(db):
    facility_data = FacilityAdd(title="Temp Facility")
    facility = await db.facilities.add(facility_data)
    await db.commit()

    await db.facilities.delete(id=facility.id)
    await db.commit()

    fetched = await db.facilities.get_one_or_none(id=facility.id)
    assert fetched is None


async def test_facility_db_edit(db):
    facility_data = FacilityAdd(title="Rename Me")
    facility = await db.facilities.add(facility_data)
    await db.commit()

    updated_data = FacilityAdd(title="Renamed")
    await db.facilities.edit(updated_data, id=facility.id)
    await db.commit()

    fetched = await db.facilities.get_one(id=facility.id)
    assert fetched.title == "Renamed"


async def test_rooms_facilities_set(db):
    facility = await db.facilities.add(FacilityAdd(title="Pool"))
    await db.commit()

    room_data = RoomAdd(hotel_id=1, title="Room w Facilities", description=None, price=10000, quantity=1)
    room = await db.rooms.add(room_data)
    await db.commit()

    repo = RoomsFacilitiesRepository(db.session)
    await repo.set_room_facilities(room.id, [facility.id])
    await db.commit()

    rooms_with_rels = await db.rooms.get_one_with_rels(id=room.id, hotel_id=1)
    facilities_ids = [f.id for f in rooms_with_rels.facilities]
    assert facility.id in facilities_ids


async def test_rooms_facilities_clear(db):
    facility = await db.facilities.add(FacilityAdd(title="Gym"))
    await db.commit()

    room_data = RoomAdd(hotel_id=1, title="Room w Facilities2", description=None, price=11000, quantity=1)
    room = await db.rooms.add(room_data)
    await db.commit()

    repo = RoomsFacilitiesRepository(db.session)
    await repo.set_room_facilities(room.id, [facility.id])
    await db.commit()

    await repo.set_room_facilities(room.id, [])
    await db.commit()

    rooms_with_rels = await db.rooms.get_one_with_rels(id=room.id, hotel_id=1)
    assert len(rooms_with_rels.facilities) == 0
