import io

async def test_upload_image(ac):
    file_content = io.BytesIO(b"fake image content")
    response = await ac.post(
        "/images",
        files={"file": ("test.png", file_content, "image/png")},
    )
    assert response.status_code == 200
