import logging
import requests
import tempfile
from io import BytesIO
from zipfile import ZipFile
from threading import Lock
import time
import os

from config.configuration import config
from service.bounding_box import BoundingBox

logger = logging.getLogger(__name__)


class CacheEntry:
    def __init__(self, file_path: str, expire_at: float):
        self.file_path = file_path
        self.expire_at = expire_at
        self.last_access = time.time()

class DTMService:
    """
    Service for fetching and caching DTM files (xyz from .zip), with on-access cleanup and total cache size management.
    """

    FILE_TTL_SECONDS = 3600
    MAX_CACHE_ITEMS = 32


    def __init__(self) -> None:
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = self.temp_dir_obj.name
        self.cache_lock = Lock()
        self.file_cache: dict[str, CacheEntry] = {}

    def cleanup_expired_and_overflow(self):
        """
        Cleans up expired and excess entries from the file cache.
        """
        now = time.time()
        expired_keys = [k for k, v in self.file_cache.items() if v.expire_at < now or not os.path.exists(v.file_path)]
        for k in expired_keys:
            entry = self.file_cache[k]
            try:
                if os.path.exists(entry.file_path):
                    os.remove(entry.file_path)
                    logger.info(f"Removed expired DTM file from disk: {entry.file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove expired file {entry.file_path}: {e}")
            del self.file_cache[k]
        while len(self.file_cache) > self.MAX_CACHE_ITEMS:
            oldest_key, oldest_entry = min(self.file_cache.items(), key=lambda item: item[1].last_access)
            try:
                if os.path.exists(oldest_entry.file_path):
                    os.remove(oldest_entry.file_path)
                    logger.info(f"Evicted (max items) DTM file from disk: {oldest_entry.file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove evicted file {oldest_entry.file_path}: {e}")
            del self.file_cache[oldest_key]


    def fetch_asset_metadata(self, bounding_box: BoundingBox) -> list[dict]:
        """
        Fetch features metadata for a bounding box.
        """
        bbox_str = bounding_box.get_wgs84_bounding_box_as_string()
        logger.debug(f"Fetching STAC items for bbox: {bbox_str}")
        resp = requests.get(config.stac_api, params={"bbox": bbox_str}, timeout=10)
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
                    and asset.get("eo:gsd") == config.grid_size
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
        """
        Download and extract a DTM .xyz file from a ZIP.
        Per-file caching with TTL, cache item management, and disk cleanup.
        """
        filename = os.path.basename(asset_href).replace('.zip', '')
        with self.cache_lock:
            self.cleanup_expired_and_overflow()
            entry = self.file_cache.get(filename)
            now = time.time()
            if entry and entry.expire_at > now and os.path.exists(entry.file_path):
                entry.last_access = now
                entry.expire_at = now + self.FILE_TTL_SECONDS
                logger.debug(f"Using cached DTM file {filename}")
                return entry.file_path
            if entry:
                try:
                    if os.path.exists(entry.file_path):
                        os.remove(entry.file_path)
                        logger.info(f"Removed expired DTM file at cache fetch: {entry.file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove expired file: {entry.file_path}: {e}")
                del self.file_cache[filename]

        logger.debug(f"Downloading asset from {asset_href}")
        resp = requests.get(asset_href, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"requesting assets failed with HTTP error {resp.status_code}")
        with ZipFile(BytesIO(resp.content)) as zip_file:
            file_name = zip_file.namelist()[0]
            file_path = zip_file.extract(member=file_name, path=self.temp_dir)

        with self.cache_lock:
            now = time.time()
            expire_at = now + self.FILE_TTL_SECONDS
            self.file_cache[filename] = CacheEntry(file_path, expire_at)
            self.cleanup_expired_and_overflow()
        logger.info(f"Cached new DTM file {filename}")
        return file_path
