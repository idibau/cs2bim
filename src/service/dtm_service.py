import logging
import os
import requests
import time
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from config.configuration import config
from service.bounding_box import BoundingBox
from service.file_cache import FileCache

logger = logging.getLogger(__name__)


class DTMService:
    """
    Service for fetching and caching DTM files (xyz from .zip), with on-access cleanup and total cache size management.
    """

    FILE_TTL_SECONDS = 3600

    def __init__(self) -> None:
        self.dtm_cache_dir = "/workspace/dtm_cache"
        self.file_cache = FileCache()

    def fetch_asset_metadata(self, bounding_box: BoundingBox) -> list[dict]:
        """
        Fetch features metadata for a bounding box.
        """
        bbox_str = bounding_box.get_wgs84_bounding_box_as_string()
        logger.debug(f"Fetching STAC items for bbox: {bbox_str}")
        resp = requests.get(config.dtm.stac_api, params={"bbox": bbox_str}, timeout=10)
        logger.debug(f"STAC items request: {resp.url}")
        if resp.status_code != 200:
            raise Exception(f"requesting items failed with HTTP error {resp.status_code}")
        features = resp.json().get("features", [])
        return features

    def fetch_dtm_files(self, bounding_box: BoundingBox) -> list[str]:
        """
        Return DTM .xyz file paths for a bounding box.
        Only DTM file paths (not bbox) are cached, cache is cleaned on every access, and total size is managed.
        """
        file_paths = []
        logger.info(f"Fetching DTM files for bounding box: {bounding_box}")
        features = self.fetch_asset_metadata(bounding_box)
        for feature in features:
            assets = list(feature["assets"].values())
            asset_filter = lambda asset: (
                    asset["type"] == "application/x.ascii-xyz+zip"
                    and asset.get("eo:gsd") == config.tin.grid_size
            )
            filtered_assets = list(filter(asset_filter, assets))
            if len(filtered_assets) != 1:
                logger.error(f"Filtering assets returned {len(filtered_assets)} results, expected 1.")
                raise Exception("filtering assets returned more than one result")
            asset_href = filtered_assets[0]["href"]
            file_path = self.fetch_and_extract_xyz(asset_href)
            file_paths.append(file_path)
        return file_paths

    def fetch_and_extract_xyz(self, asset_href: str) -> str:
        file_id = os.path.basename(asset_href)

        entry = self.file_cache.get(file_id)
        if entry:
            if entry.expire_at > time.time():
                if Path(entry.file_path).exists():
                    logger.debug(f"Using cached DTM file: {file_id}")
                    return entry.file_path
                else:
                    logger.debug(f"Cached DTM file expired: {file_id}")
                    self.file_cache.delete(file_id)
            else:
                logger.debug(f"Removed expired DTM file at cache fetch: {file_id}")
                self.file_cache.delete(file_id)
                Path(entry.file_path).unlink(missing_ok=True)

        logger.debug(f"Downloading asset from {asset_href}")

        resp = requests.get(asset_href, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"requesting assets failed with HTTP error {resp.status_code}")
        with ZipFile(BytesIO(resp.content)) as zip_file:
            file_name = zip_file.namelist()[0]
            file_path = zip_file.extract(member=file_name, path=self.dtm_cache_dir)
            self.file_cache.add(file_id, file_path, self.FILE_TTL_SECONDS)

        logger.info(f"Cached new DTM file {file_id}")
        return file_path
