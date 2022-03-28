from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from app.database import PropertyModel
from app.utils.datatypes import GeoJsonPayload
from app.objects.property import Property


app = FastAPI()


@app.get("/display/{id}")
def display_property_image(id: str):
    # Select image from database
    prop = Property(id)
    image_path: Optional[str] = prop.download_image()

    if image_path is not None:
        return FileResponse(image_path, media_type="image/jpg")

    raise HTTPException(status_code=404, detail="Image not found")


@app.post("/find")
def find_property(geojson: GeoJsonPayload):
    # Find property by geocode_geo
    if geojson.location.type != "Point":
        raise HTTPException(status_code=400, detail="Invalid location type")

    return PropertyModel.find_by_geocode_geo(geojson)


@app.get("/statistics/{id}")
def get_statistics(id: str, zone_size_m: int = 10):
    # Get statistics for a property
    prop = Property(id)
    stats = prop.get_statistics(zone_size_m)
    if stats is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return stats


@app.get("/list")
def get_all(size: int = Query(10, ge=1, le=1000), page: int = Query(1, ge=1)):
    # Get list of properties
    props = PropertyModel.get_all(size, page)
    if props is None:
        raise HTTPException(status_code=404, detail="No properties found")

    return props
