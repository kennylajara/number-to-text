# Zesty.ai Back-End Engineering Test

API created as Technical Assessment to apply for the Backend Developer position at [Zesty.ai](https://zesty.ai).

**[Working demo](http://45.79.199.22/)**

## Requirments

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- make (On Ubuntu `sudo apt-get install build-essential`)

## API Specification

You will find the the API documentation at the root directory.

---

### GET /list

_Fetches and displays property image (as JPEG) by ID_

`example: GET localhost:3000/list`

##### Request Parameters

- None

##### Response

JSON listing properties ID.

---

### GET /display/:id

_Fetches and displays property image (as JPEG) by ID_

`example: GET localhost:3000/display/f853874999424ad2a5b6f37af6b56610`

##### Request Parameters

- `id` | description: Property ID | type: string | required: true

##### Response

JPEG image

---

### POST /find

_Finds properties within X meters away from provided geojson point._

`example: POST localhost:3000/find`

##### Request Body

JSON object with the following properties

- `location` | geojson object representing point to search from | required: true | validation: geojson | type: object
- `distance` | distance, in meters, to search from `location` | required: true | validation: greater than 0, less than some reasonable number | type: float

```
example:

{
  "location": {
    "type": "Point",
    "coordinates": [-80.0782213, 26.8849731]
  },
  "distance": 500
}
```

##### Response

JSON array with objects containing at least the following fields (you may include more if you think they would be helpful)

- `property_id` | ID of property object
- `distance_m` | actual distance from input `distance`

---

### GET /statistics/:id?zone_size_m

_Returns various statistics for parcels and buildings found X meters around the requested property_

`example: GET localhost:1235/statistics/f853874999424ad2a5b6f37af6b56610?zone_size_m=10`

##### Request Parameters

- `id` | description: Property ID | type: string | required: true | validation: length greater than 0
- `zone_size_m` | description: Buffer distance used for calculating zones | type: integer | required: true | validation: greater than 0

##### Response

JSON object including following fields

- `parcel_area_sqm` | description: total area of the property's parcel, in square meters | type: float
- `building_area_sqm` | description: total area of building, in square meters | type: float
- `building_distance_m` | description: distance from the centroid of the property, to the centroid of building, in meters | type: float
- `zone_density` | description: density (%) of building's area to zone area (the zone is the `geocode_geo` with a buffer/circle with the radius of `zone_size_m` input) |
  type: float

---

## Development

To deploy for development environment, make a copy of `.env-sample` and name it `.env`. Then, run de following command:

```
make dev
```

To run the test suite in the containers, after the previous command, run:

```
make test
```

To stop de containers, run:

```
make stop
```

## Deploy

To deploy on a production environment, make a copy of `.env-sample`, name it `.env` and change the value of the database credentials. Then, run the following command:

```
make up
```

To stop de containers run:

```
make down
```
