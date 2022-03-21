import os
from turtle import distance

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import requests

from app.models import Property, GeoJsonPayload
from app.database import conn

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
