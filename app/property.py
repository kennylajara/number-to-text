import sys
from typing import Optional

from app.database import conn


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
            """SELECT id, geocode_geo, parcel_geo, building_geo, image_bounds, image_url FROM properties WHERE id = %s""",
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

    def _get_image_path(self, id: Optional[str]):
        if not id:
            return None
        return f"/tmp/{id}.jpg"
