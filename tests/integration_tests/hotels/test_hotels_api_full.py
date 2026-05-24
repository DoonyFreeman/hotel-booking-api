import pytest


@pytest.mark.parametrize("title, location, status_code", [
    ("New Hotel", "New York", 200),
    ("", "Nowhere", 200),
])
async def test_create_hotel(ac, title, location, status_code):
    response = await ac.post(
        "/hotels",
        json={"title": title, "location": location},
    )
    assert response.status_code == status_code
    if status_code == 200:
        data = response.json()
        assert data["status"] == "OK"
        assert data["hotel"]["title"] == title


async def test_get_hotel_by_id(ac):
    response = await ac.get("/hotels/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "title" in data
    assert "location" in data


async def test_get_hotel_not_found(ac):
    response = await ac.get("/hotels/99999")
    assert response.status_code == 404


async def test_put_hotel(ac):
    response = await ac.put(
        "/hotels/1",
        json={"title": "Updated Hotel", "location": "Updated Location"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

    get_response = await ac.get("/hotels/1")
    assert get_response.json()["title"] == "Updated Hotel"


async def test_patch_hotel(ac):
    response = await ac.patch(
        "/hotels/2",
        json={"title": "Patched Title"},
    )
    assert response.status_code == 200

    get_response = await ac.get("/hotels/2")
    assert get_response.json()["title"] == "Patched Title"


async def test_delete_hotel(ac):
    create_resp = await ac.post(
        "/hotels",
        json={"title": "Temp Hotel", "location": "Temp Loc"},
    )
    hotel_id = create_resp.json()["hotel"]["id"]

    delete_resp = await ac.delete(f"/hotels/{hotel_id}")
    assert delete_resp.status_code == 200

    get_resp = await ac.get(f"/hotels/{hotel_id}")
    assert get_resp.status_code == 404


async def test_get_hotels_filtered(ac):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2026-06-01",
            "date_to": "2026-06-10",
            "title": "altay",
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
