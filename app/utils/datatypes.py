from pydantic import BaseModel, Field, NonNegativeFloat


class GeoJsonLocation(BaseModel):
    coordinates: list[float] = Field(..., alias="coordinates")
    type: str


class GeoJsonPayload(BaseModel):
    distance: NonNegativeFloat
    location: GeoJsonLocation


class Statistics(BaseModel):
    id: str
    parcel_area_sqm: NonNegativeFloat
    building_area_sqm: NonNegativeFloat
    building_distance_m: NonNegativeFloat
    zone_density: NonNegativeFloat
