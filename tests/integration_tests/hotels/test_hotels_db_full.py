from src.schemas.hotels import HotelAdd, HotelPATCH
from src.exceptions import ObjectNotFoundException


async def test_hotel_db_add_and_get(db):
    hotel_data = HotelAdd(title="DB Hotel", location="DB Location")
    hotel = await db.hotels.add(hotel_data)
    await db.commit()

    assert hotel.id is not None
    assert hotel.title == "DB Hotel"

    fetched = await db.hotels.get_one(id=hotel.id)
    assert fetched.title == "DB Hotel"
    assert fetched.location == "DB Location"


async def test_hotel_db_edit(db):
    hotel_data = HotelAdd(title="Editable", location="Loc")
    hotel = await db.hotels.add(hotel_data)
    await db.commit()

    updated_data = HotelAdd(title="Edited", location="New Loc")
    await db.hotels.edit(updated_data, id=hotel.id)
    await db.commit()

    hotel = await db.hotels.get_one(id=hotel.id)
    assert hotel.title == "Edited"
    assert hotel.location == "New Loc"


async def test_hotel_db_partial_update(db):
    hotel_data = HotelAdd(title="Partial", location="Partial Loc")
    hotel = await db.hotels.add(hotel_data)
    await db.commit()

    patch_data = HotelPATCH(title="Partially Updated")
    await db.hotels.edit(patch_data, exclude_unset=True, id=hotel.id)
    await db.commit()

    hotel = await db.hotels.get_one(id=hotel.id)
    assert hotel.title == "Partially Updated"
    assert hotel.location == "Partial Loc"


async def test_hotel_db_delete(db):
    hotel_data = HotelAdd(title="Deletable", location="To Delete")
    hotel = await db.hotels.add(hotel_data)
    await db.commit()

    await db.hotels.delete(id=hotel.id)
    await db.commit()

    fetched = await db.hotels.get_one_or_none(id=hotel.id)
    assert fetched is None


async def test_hotel_db_get_one_raises(db):
    import pytest
    with pytest.raises(ObjectNotFoundException):
        await db.hotels.get_one(id=99999)


async def test_hotel_db_get_filtered(db):
    all_hotels = await db.hotels.get_filtered()
    assert len(all_hotels) >= 3


async def test_hotel_db_get_all(db):
    all_hotels = await db.hotels.get_all()
    assert len(all_hotels) >= 3
