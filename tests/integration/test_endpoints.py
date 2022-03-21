import os

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@app.on_event("startup")
def startup():
    filename = "/tmp/f853874999424ad2a5b6f37af6b56610.jpg"
    if os.path.exists(filename):
        os.remove(filename)


def test_endpoint_display_with_invalid_id():
    response = client.get("/display/invalid")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": "Image not found in database"}


def test_endpoint_display_with_downloaded_image():
    response = client.get("/display/f1650f2a99824f349643ad234abff6a2")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpg"


def test_endpoint_display_with_not_downloaded_image():
    response = client.get("/display/f853874999424ad2a5b6f37af6b56610")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpg"
