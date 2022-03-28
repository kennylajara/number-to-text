from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


#
#  GET /display/{id}
#


def test_endpoint_display_with_non_existing_id():
    response = client.get("/display/invalid")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": "Image not found"}


def test_endpoint_display_with_existing_id():
    # Two times: one with the image in the database that needs to
    # be downloaded, and one after downloading the image.
    for _ in range(2):
        response = client.get("/display/f1650f2a99824f349643ad234abff6a2")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpg"


#
#  POST /find
#


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


#
#  GET /statistics/{id}
#


def test_endpoint_statistics_with_non_existing_id():
    response = client.get("/statistics/invalid")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": "Property not found"}


def test_endpoint_statistics_with_existing_id():
    response = client.get("/statistics/f853874999424ad2a5b6f37af6b56610")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "id": "f853874999424ad2a5b6f37af6b56610",
        "parcel_area_sqm": 1493.818154175693,
        "building_area_sqm": 728.4045420035836,
        "building_distance_m": 8.69754852,
        "zone_density": 2.332165709432774,
    }


def test_endpoint_statistics_with_zone_size_m():
    response = client.get(
        "/statistics/f853874999424ad2a5b6f37af6b56610?zone_size_m=100"
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "id": "f853874999424ad2a5b6f37af6b56610",
        "parcel_area_sqm": 1493.818154175693,
        "building_area_sqm": 728.4045420035836,
        "building_distance_m": 8.69754852,
        "zone_density": 0.023321657486992376,
    }


#
#  GET /list
#


def test_endpoint_list():
    response = client.get("/list")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == [
        "f1650f2a99824f349643ad234abff6a2",
        "f853874999424ad2a5b6f37af6b56610",
        "3290ec7dd190478aab124f6f2f32bdd7",
        "5e25c841f0ca47ac8215b5fd0076259a",
        "622088210a6f43fca2a1824e8610df03",
    ]


def test_endpoint_list_with_page_lower_than_min_page():
    response = client.get("/list?page=0")
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "page"],
                "msg": "ensure this value is greater than or equal to 1",
                "type": "value_error.number.not_ge",
                "ctx": {"limit_value": 1},
            }
        ]
    }


def test_endpoint_list_with_size_lower_than_min_size():
    response = client.get("/list?size=0")
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "size"],
                "msg": "ensure this value is greater than or equal to 1",
                "type": "value_error.number.not_ge",
                "ctx": {"limit_value": 1},
            }
        ]
    }


def test_endpoint_list_with_page_greater_than_max_size():
    response = client.get("/list?size=1001")
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "detail": [
            {
                "loc": ["query", "size"],
                "msg": "ensure this value is less than or equal to 1000",
                "type": "value_error.number.not_le",
                "ctx": {"limit_value": 1000},
            }
        ]
    }


def test_endpoint_list_with_correct_page_and_size_parameters():
    tests = [
        {
            "size": 2,
            "page": 1,
            "results": [
                "f1650f2a99824f349643ad234abff6a2",
                "f853874999424ad2a5b6f37af6b56610",
            ],
        },
        {
            "size": 2,
            "page": 2,
            "results": [
                "3290ec7dd190478aab124f6f2f32bdd7",
                "5e25c841f0ca47ac8215b5fd0076259a",
            ],
        },
        {
            "size": 2,
            "page": 3,
            "results": ["622088210a6f43fca2a1824e8610df03"],
        },
        {
            "size": 3,
            "page": 1,
            "results": [
                "f1650f2a99824f349643ad234abff6a2",
                "f853874999424ad2a5b6f37af6b56610",
                "3290ec7dd190478aab124f6f2f32bdd7",
            ],
        },
        {
            "size": 3,
            "page": 2,
            "results": [
                "5e25c841f0ca47ac8215b5fd0076259a",
                "622088210a6f43fca2a1824e8610df03",
            ],
        },
    ]

    for test in tests:
        response = client.get(f"/list?page={test['page']}&size={test['size']}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.json() == test["results"]


def test_endpoint_list_with_no_results():
    response = client.get("/list?page=100&size=100")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"detail": "No properties found"}
