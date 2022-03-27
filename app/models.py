from tkinter.messagebox import NO
from typing import Optional
from xml.sax.handler import all_properties

from pydantic import BaseModel, Field

from app.database import conn


class GeoJsonLocation(BaseModel):
    coordinates: tuple[float, float]
    type: str


class GeoJsonPayload(BaseModel):
    distance: float = Field(..., gt=0.0)
    location: GeoJsonLocation


class Statistics(BaseModel):
    id: str
    parcel_area_sqm: float
    building_area_sqm: float
    building_distance_m: float
    zone_density: float


class Property:
    def __init__(self, id: Optional[str] = None) -> None:
        self._id: Optional[str] = id
        self._geocode_geo: Optional[str] = None
        self._parcel_lat: Optional[str] = None
        self._building_geo: Optional[str] = None
        self._image_bounds: Optional[str] = None
        self._image_url: Optional[str] = None

        if id:
            self.get_by_id(id)

    def get_by_id(self, id: str) -> None:
        cur = conn.cursor()
        cur.execute(
            """
                SELECT id, geocode_geo, parcel_geo, building_geo, image_bounds, image_url 
                FROM properties 
                WHERE id = %s
            """,
            (id,),
        )
        result = cur.fetchone()

        if result:
            self._id = result[0]
            self._geocode_geo = result[1]
            self._parcel_geo = result[2]
            self._building_geo = result[3]
            self._image_bounds = result[4]
            self._image_url = result[5]
        else:
            self._id = None
            self._geocode_geo = None
            self._parcel_geo = None
            self._building_geo = None
            self._image_bounds = None
            self._image_url = None

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def geocode_geo(self) -> Optional[str]:
        return self._geocode_geo

    @property
    def parcel_geo(self) -> Optional[str]:
        return self._parcel_geo

    @property
    def building_geo(self) -> Optional[str]:
        return self._building_geo

    @property
    def image_bounds(self) -> Optional[str]:
        return self._image_bounds

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @property
    def image_path(self) -> Optional[str]:
        return self._get_image_path(self._id)

    @staticmethod
    def find_by_geocode_geo(geojson: GeoJsonPayload) -> Optional[list]:

        point_lon, point_lat = geojson.location.coordinates
        distance_threshold = geojson.distance

        # Look for properties within distance_threshold of point
        cur = conn.cursor()
        cur.execute(
            """
                SELECT id, geocode_geo, parcel_geo, building_geo, image_bounds, image_url 
                FROM properties 
                WHERE ST_DWithin(geocode_geo, ST_GeomFromText(%s, 4326), %s)
            """,
            (f"POINT({point_lon} {point_lat})", distance_threshold),
        )
        result = cur.fetchall()

        if not result:
            return []

        # Return properties
        return [
            {
                "id": row[0],
                "geocode_geo": row[1],
                "parcel_geo": row[2],
                "building_geo": row[3],
                "image_bounds": row[4],
                "image_url": row[5],
            }
            for row in result
        ]

    def get_statistics(self, zone_size_m: int = 10) -> Optional[Statistics]:
        """Returns various statistics for parcels and buildings found X meters around the requested property"""
        query_statitics = f"""
            SELECT 
                ST_Area(parcel_geo),
                ST_Area(building_geo),
                ST_Distance(geocode_geo, ST_Centroid(building_geo)),
                ST_Area(building_geo)/ST_Area(ST_Buffer(geocode_geo, {zone_size_m}))   
            FROM properties  AS p
            WHERE p.id = '{self._id}'
        """
        cur = conn.cursor()
        cur.execute(query_statitics)
        result = cur.fetchone()

        if not result:
            return None

        return Statistics(
            id=self._id,
            parcel_area_sqm=result[0],
            building_area_sqm=result[1],
            building_distance_m=result[2],
            zone_density=result[3],
        )

    def _get_image_path(self, id: Optional[str]):
        if not id:
            return None
        return f"/tmp/{id}.jpg"
