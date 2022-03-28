from pydantic import BaseModel, Field


class GeoJsonLocation(BaseModel):
    coordinates: tuple[float, float]
    type: str


class GeoJsonPayload(BaseModel):
    distance: float = Field(..., gt=0.0)
    location: GeoJsonLocation


class Statistics(BaseModel):
    id: str
    parcel_area_sqm: float = Field(..., gt=0.0)
    building_area_sqm: float = Field(..., gt=0.0)
    building_distance_m: float = Field(..., gt=0.0)
    zone_density: float = Field(..., gt=0.0)
