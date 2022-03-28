import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from PIL import Image
import requests

from app.models import Property, GeoJsonPayload

app = FastAPI()


@app.get("/display/{id}")
def read_root(id: str):
    # Select image from database
    prop = Property(id)

    if prop.image_url is None:
        raise HTTPException(status_code=404, detail="Image not found in database")

    # Return image if already downloaded
    image_path = str(prop.image_path)
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpg")

    # Download image
    res = requests.get(prop.image_url, stream=True)
    if res.status_code == 200:
        Image.open(res.raw).convert("RGB").save(image_path)
        return FileResponse(image_path, media_type="image/jpg")

    raise HTTPException(status_code=404, detail="Image not found on cloud storage")


@app.post("/find")
def find_property(geojson: GeoJsonPayload):
    # Find property by geocode_geo
    if geojson.location.type != "Point":
        raise HTTPException(status_code=400, detail="Invalid location type")

    return Property.find_by_geocode_geo(geojson)


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
    props = Property.get_all(size, page)
    if props is None:
        raise HTTPException(status_code=404, detail="No properties found")

    return props
