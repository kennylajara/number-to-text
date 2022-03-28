from typing import Optional

from fastapi import Body, FastAPI, HTTPException, Path, Query
from fastapi.responses import FileResponse

from app.database import PropertyModel
from app.utils.datatypes import GeoJsonPayload
from app.objects.property import Property


description = """
An API for accessing property data.
This API has been created as part of the assessment for the position of Backend Developer at Zesty.ai.
"""

tags_metadata = [
    {
        "name": "Properties",
        "description": "Operations related to properties",
    },
]

app = FastAPI(
    title="Property Data API",
    description=description,
    version="0.1.0",
    tags_metadata=tags_metadata,
    redoc_url="/",
)


@app.get("/list", tags=["Properties"])
def get_all_the_properties(
    size: int = Query(
        10, ge=1, le=1000, description="Number of properties to return per page"
    ),
    page: int = Query(1, ge=1, description="Page number"),
):
    """
    Returns a list of all the properties in the database.
    """
    props = PropertyModel.get_all(size, page)
    if props is None:
        raise HTTPException(status_code=404, detail="No properties found")

    return props


@app.get("/statistics/{id}", tags=["Properties"])
def get_statistics_of_property(
    id: str = Path(..., description="Property ID"),
    zone_size_m: int = Query(10, description="Zone size in meters"),
):
    """
    Returns various statistics for parcels and buildings found X meters around the requested property.
    """
    prop = Property(id)
    stats = prop.get_statistics(zone_size_m)
    if stats is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return stats


@app.get("/display/{id}", tags=["Properties"])
def display_a_property_image(id: str = Path(..., description="Property ID")):
    """
    Fetches and displays property image (as JPEG) by ID.
    """
    prop = Property(id)
    image_path: Optional[str] = prop.download_image()

    if image_path is not None:
        return FileResponse(image_path, media_type="image/jpg")

    raise HTTPException(status_code=404, detail="Image not found")


@app.post(
    "/find",
    tags=["Properties"],
)
def find_properties_by_geojson(
    geojson: GeoJsonPayload = Body(..., description="GeoJSON point")
):
    """
    Finds properties within X meters away from provided geojson point.
    """
    if geojson.location.type != "Point":
        raise HTTPException(status_code=400, detail="Invalid location type")

    return PropertyModel.find_by_geocode_geo(geojson)
