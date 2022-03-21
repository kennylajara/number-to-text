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


def test_endpoint_find_with_invalid_geojson():
    response = client.post("/find", json={"location": {"type": "invalid"}})
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "distance"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["body", "location", "coordinates"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ]
    }


def test_endpoint_find_with_invalid_geojson_coordinates():
    response = client.post(
        "/find", json={"location": {"type": "Point", "coordinates": []}}
    )
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "distance"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["body", "location", "coordinates"],
                "msg": "wrong tuple length 0, expected 2",
                "type": "value_error.tuple.length",
                "ctx": {"actual_length": 0, "expected_length": 2},
            },
        ]
    }


def test_endpoint_find_with_invalid_distance():
    response = client.post(
        "/find",
        json={"location": {"type": "Point", "coordinates": [1.0, 1.0]}, "distance": -1},
    )
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "distance"],
                "msg": "ensure this value is greater than 0.0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0.0},
            }
        ]
    }


def test_endpoint_find_with_valid_data_but_no_results():
    response = client.post(
        "/find",
        json={
            "location": {"type": "Point", "coordinates": [-50.0, 26.8]},
            "distance": 500,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == []


def test_endpoint_find_with_valid_data_and_result():
    response = client.post(
        "/find",
        json={
            "location": {"type": "Point", "coordinates": [-80.0782213, 26.8849731]},
            "distance": 500,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == [
        {
            "id": "3290ec7dd190478aab124f6f2f32bdd7",
            "geocode_geo": {"x": -80.0782213, "y": 26.8849731},
            "parcel_geo": {},
            "building_geo": {},
            "image_bounds": [
                -80.07864028215408,
                26.88459934588957,
                -80.07780209183693,
                26.885346941040712,
            ],
            "image_url": "https://storage.googleapis.com/engineering-test/images/3290ec7dd190478aab124f6f2f32bdd7.tif",
        }
    ]
