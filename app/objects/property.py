import os
from typing import Optional

from app.database import PropertyModel
from app.utils.datatypes import Statistics


class Property:
    def __init__(self, id: Optional[str] = None) -> None:
        self._id: Optional[str] = id
        self._geocode_geo: Optional[str] = None
        self._parcel_geo: Optional[str] = None
        self._building_geo: Optional[str] = None
        self._image_bounds: Optional[str] = None
        self._image_url: Optional[str] = None

        if id:
            result = PropertyModel.get_by_id(id)
            if result:
                self._id = result["id"]
                self._geocode_geo = result["geocode_geo"]
                self._parcel_geo = result["parcel_geo"]
                self._building_geo = result["building_geo"]
                self._image_bounds = result["image_bounds"]
                self._image_url = result["image_url"]

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

    def download_image(self) -> Optional[str]:
        """Downloads the image for the property (if not already downloaded) and returns the path to the image"""
        image_path: Optional[str]

        if self.image_url is None:
            return None

        # Return image if already downloaded
        image_path = str(self.image_path)
        if os.path.exists(image_path):
            return image_path

        # Download image and return image if not already downloaded
        image_path = self._download_image()
        if image_path is not None:
            return image_path

        return None

    def get_statistics(self, zone_size_m: int = 10) -> Optional[Statistics]:
        """Returns various statistics for parcels and buildings found X meters around the requested property"""
        if not self._id:
            return None

        return PropertyModel.get_statistics(self._id, zone_size_m)

    def _download_image(self) -> Optional[str]:
        """Downloads the image for the property"""
        from PIL import Image
        import requests

        res = requests.get(str(self.image_url), stream=True)
        if res.status_code == 200:
            image_path = self._get_image_path(self._id)
            Image.open(res.raw).convert("RGB").save(image_path)
            return image_path

        return None

    def _get_image_path(self, id: Optional[str]):
        if not id:
            return None

        return f"/tmp/{id}.jpg"
