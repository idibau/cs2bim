import logging
import os
import requests
import time
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from dateutil import parser

from config.configuration import config
from service.bounding_box import BoundingBox
from service.file_cache import FileCache

logger = logging.getLogger(__name__)


class STACService:
    """
    Service for fetching and caching files from a stac api, with on-access cache cleanup.
    """

    FILE_TTL_SECONDS = 86400

    def __init__(self) -> None:
        self.cache_dir = "/workspace/cache"
        self.file_cache = FileCache()

    def fetch_city_gml_assets(self, bounding_box: BoundingBox):
        asset_filter = lambda asset: asset["type"] == "application/x.gml+zip"
        hrefs = self.fetch_latest_assets(config.stac.building_items_url, bounding_box, asset_filter)
        return [self.fetch_and_extract_zip(href) for href in hrefs]

    def fetch_dtm_assets(self, bounding_box: BoundingBox, grid_size: float):
        asset_filter = lambda asset: asset["type"] == "application/x.ascii-xyz+zip" and asset[
            "eo:gsd"] == grid_size
        hrefs = self.fetch_latest_assets(config.stac.dtm_items_url, bounding_box, asset_filter)
        return [self.fetch_and_extract_zip(href) for href in hrefs]

    def fetch_features(self, stac_collection_items_url: str, bounding_box: BoundingBox) -> list[dict]:
        """
        Fetch features metadata for a bounding box.
        """
        bbox_str = bounding_box.get_wgs84_bounding_box_as_string()
        logger.debug(f"Fetching STAC items for bbox: {bbox_str}")
        resp = requests.get(stac_collection_items_url, params={"bbox": bbox_str}, timeout=10)
        logger.debug(f"STAC items request: {resp.url}")
        if resp.status_code != 200:
            raise Exception(f"requesting items failed with HTTP error {resp.status_code}")
        features = resp.json().get("features", [])
        return features

    def fetch_latest_assets(self, stac_collection_items_url, bounding_box: BoundingBox, asset_filter) -> list[str]:
        feature_assets = {}
        feature_datetimes = {}

        features = self.fetch_features(stac_collection_items_url, bounding_box)
        for feature in features:
            feature_datetime = parser.isoparse(feature["properties"]["datetime"])
            assets = list(feature["assets"].values())
            filtered_assets = list(filter(asset_filter, assets)) if not asset_filter is None else assets
            if filtered_assets:
                if len(filtered_assets) != 1:
                    logger.error(f"Filtering assets returned {len(filtered_assets)} results, expected 1.")
                    raise Exception("filtering assets returned more than one result")
                bbox = str(feature["bbox"])
                if bbox not in feature_assets or feature_datetime > feature_datetimes[bbox]:
                    feature_assets[bbox] = filtered_assets[0]
                    feature_datetimes[bbox] = feature_datetime

        return [asset["href"] for asset in feature_assets.values()]

    def fetch_and_extract_zip(self, zip_href: str) -> str:
        file_id = os.path.basename(zip_href)

        entry = self.file_cache.get(file_id)
        if entry:
            if entry.expire_at > time.time():
                if Path(entry.file_path).exists():
                    logger.debug(f"Using cached file: {file_id}")
                    return entry.file_path
                else:
                    logger.debug(f"Cached file expired: {file_id}")
                    self.file_cache.delete(file_id)
            else:
                logger.debug(f"Removed expired file at cache fetch: {file_id}")
                self.file_cache.delete(file_id)
                Path(entry.file_path).unlink(missing_ok=True)

        logger.debug(f"Downloading asset from {zip_href}")

        resp = requests.get(zip_href, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"requesting assets failed with HTTP error {resp.status_code}")
        with ZipFile(BytesIO(resp.content)) as zip_file:
            file_name = zip_file.namelist()[0]
            file_path = zip_file.extract(member=file_name, path=self.cache_dir)
            self.file_cache.add(file_id, file_path, self.FILE_TTL_SECONDS)

        logger.info(f"Cached new file {file_id}")
        return file_path
