import logging
import os
import requests
from dateutil import parser
from io import BytesIO
from typing import Callable
from zipfile import ZipFile

from config.configuration import config
from service.bounding_box import BoundingBox
from service.file_cache import FileCache

logger = logging.getLogger(__name__)


class STACService:
    """
    Service class for interacting with SpatioTemporal Asset Catalog (STAC) endpoints, retrieving geospatial assets,
    and caching downloaded files.
    """

    FILE_TTL_SECONDS = 86400

    def __init__(self):
        self.cache_dir = "/workspace/cache"
        self.file_cache = FileCache()

    def fetch_city_gml_assets(self, bounding_box: BoundingBox) -> list[str]:
        """
        Retrieves and extracts CityGML (GML ZIP) asset files from the STAC endpoint that intersect
        with the specified bounding box.

        Args:
           bounding_box: The bounding box used to query features.

        Returns:
           List of file paths to the extracted CityGML files.
        """
        asset_filter = lambda asset: asset["type"] == "application/x.gml+zip"
        hrefs = self.fetch_latest_assets(config.stac.building_items_url, bounding_box, asset_filter)
        return [self.fetch_and_extract_zip(href, "gml") for href in hrefs]

    def fetch_dtm_assets(self, bounding_box: BoundingBox, grid_size: float) -> list[str]:
        """
        Retrieves and extracts DTM (ASCII XYZ ZIP) asset files from the STAC endpoint that intersect
        with the specified bounding box and match the grid size.

        Args:
            bounding_box: The bounding box used to query features.
            grid_size: Desired ground sampling distance for the DTM assets.

        Returns:
            List of file paths to the extracted DTM files.
        """
        asset_filter = lambda asset: (asset["type"] == "application/x.ascii-xyz+zip" and (
                asset.get("gsd") == grid_size or asset.get("eo:gsd") == grid_size))
        hrefs = self.fetch_latest_assets(config.stac.dtm_items_url, bounding_box, asset_filter)
        return [self.fetch_and_extract_zip(href, "xyz") for href in hrefs]

    def fetch_features(self, stac_collection_items_url: str, bounding_box: BoundingBox) -> list[dict]:
        """
        Queries the STAC endpoint for features that intersect the specified bounding box.

        Args:
            stac_collection_items_url: URL to the STAC collection items endpoint.
            bounding_box: The bounding box for filtering features.

        Returns:
            List of feature dictionaries from the STAC endpoint.

        Raises:
            Exception: If the HTTP request to the endpoint fails.
        """
        bbox_str = bounding_box.get_wgs84_bounding_box_as_string()
        logger.debug(f"fetching STAC items for bbox: {bbox_str}")

        all_features = []
        url = stac_collection_items_url
        params = {"bbox": bbox_str}

        while url:
            resp = requests.get(url, params=params, timeout=60)
            logger.debug(f"STAC items request: {resp.url}")
            if resp.status_code != 200:
                raise Exception(f"requesting items failed with HTTP error {resp.status_code}")
            data = resp.json()
            all_features.extend(data.get("features", []))
            next_link = next((l for l in data.get("links", []) if l["rel"] == "next"), None)
            url = next_link["href"] if next_link else None
            params = {}

        return all_features

    def fetch_latest_assets(self, stac_collection_items_url: str, bounding_box: BoundingBox, asset_filter: Callable) -> \
    list[str]:
        """
        Retrieves the latest version of filtered assets from STAC features intersecting the bounding box.

        Args:
            stac_collection_items_url: URL to the STAC collection items endpoint.
            bounding_box: The bounding box for filtering features.
            asset_filter: Function to filter desired assets from each feature.

        Returns:
            List of asset HREFs corresponding to the latest features per bounding box.

        Raises:
            Exception: If asset filtering results in ambiguity or unexpected asset count.
        """

        feature_assets = {}
        feature_datetimes = {}

        features = self.fetch_features(stac_collection_items_url, bounding_box)
        for feature in features:
            feature_datetime = parser.isoparse(feature["properties"]["datetime"])
            assets = list(feature["assets"].values())
            filtered_assets = list(filter(asset_filter, assets)) if not asset_filter is None else assets
            if filtered_assets:
                if len(filtered_assets) != 1:
                    logger.error(f"filtering assets returned {len(filtered_assets)} results, expected 1.")
                    raise Exception("filtering assets returned more than one result")
                bbox = str(feature["bbox"])
                if bbox not in feature_assets or feature_datetime > feature_datetimes[bbox]:
                    feature_assets[bbox] = filtered_assets[0]
                    feature_datetimes[bbox] = feature_datetime

        return [asset["href"] for asset in feature_assets.values()]

    def fetch_and_extract_zip(self, zip_href: str, target_extension: str) -> str:
        """
        Downloads a ZIP file from the given URL, extracts its contents to the cache directory,
        and caches the resulting file for later reuse.

        Args:
            zip_href: HREF/URL of the remote ZIP asset.
            target_extension: expected extension

        Returns:
            File path to the extracted file in the cache directory.

        Raises:
            Exception: If the HTTP request to download the asset fails.
        """
        file_id = os.path.basename(zip_href)

        entry = self.file_cache.get(file_id)
        if entry is not None:
            return entry.file_path

        logger.debug(f"downloading asset from {zip_href}")

        resp = requests.get(zip_href, timeout=60)
        if resp.status_code != 200:
            raise Exception(f"requesting assets failed with HTTP error {resp.status_code}")

        file_path = None
        with ZipFile(BytesIO(resp.content)) as zip_file:
            all_files = zip_file.namelist()
            matching_files = [f for f in all_files if f.lower().endswith(target_extension.lower())]
            if not matching_files:
                raise Exception(f"No .{target_extension} file found in ZIP: {zip_href}")
            file_name = matching_files[0]
            if len(matching_files) > 1:
                logger.warning(f"Multiple {target_extension} files found. Using: {file_name}")
            file_path = zip_file.extract(member=file_name, path=self.cache_dir)
            self.file_cache.add(file_id, file_path, self.FILE_TTL_SECONDS)

        logger.info(f"cached new file {file_id}")
        return file_path
