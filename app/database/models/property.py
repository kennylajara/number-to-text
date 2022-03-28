from typing import Optional

from app.database.db import conn
from app.utils.datatypes import GeoJsonPayload, Statistics


class PropertyModel:
    @staticmethod
    def get_all(size: int, page: int) -> Optional[list[str]]:
        cur = conn.cursor()
        cur.execute(
            """
                SELECT id 
                FROM properties 
                LIMIT %s OFFSET %s
            """,
            (size, size * (page - 1)),
        )
        result = cur.fetchall()

        if not result:
            return None

        return [row[0] for row in result]

    @staticmethod
    def get_by_id(id: str) -> Optional[dict[str, str]]:
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

        if not result:
            return None

        return {
            "id": result[0],
            "geocode_geo": result[1],
            "parcel_geo": result[2],
            "building_geo": result[3],
            "image_bounds": result[4],
            "image_url": result[5],
        }

    @staticmethod
    def get_statistics(id: Optional[str], zone_size_m=int) -> Optional[Statistics]:
        query_statitics = f"""
            SELECT 
                ST_Area(parcel_geo),
                ST_Area(building_geo),
                ST_Distance(geocode_geo, ST_Centroid(building_geo)),
                ST_Area(building_geo)/ST_Area(ST_Buffer(geocode_geo, {zone_size_m}))   
            FROM properties AS p
            WHERE p.id = '{id}'
        """
        cur = conn.cursor()
        cur.execute(query_statitics)
        result = cur.fetchone()

        if not result:
            return None

        return Statistics(
            id=id,
            parcel_area_sqm=result[0],
            building_area_sqm=result[1],
            building_distance_m=result[2],
            zone_density=result[3],
        )

    @staticmethod
    def find_by_geocode_geo(geojson: GeoJsonPayload) -> Optional[list[dict[str, str]]]:

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
