import logging
import requests
import tempfile
from io import BytesIO
from zipfile import ZipFile

from config.configuration import config
from service.bounding_box import BoundingBox


logger = logging.getLogger(__name__)


class DTMService:
    """Service that accesses the digital terrain model api defined in the config"""

    def __init__(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def fetch_dtm_files(self, bounding_box: BoundingBox) -> list[str]:
        """Fetches all dtm files that are needed to display the area defined by the bounding box and saves them in a temporary folder"""
        file_paths = []
        items_response = requests.get(config.stac_api, params={"bbox": bounding_box.get_wgs84_bounding_box_as_string()})
        logger.debug(f"dtm request: {items_response.url}")
        if items_response.status_code == 200:
            for feature in items_response.json()["features"]:
                assets = feature["assets"].values()
                asset_filter = lambda asset: asset["type"] == "application/x.ascii-xyz+zip" and asset["eo:gsd"] == config.grid_size
                filtered_assets = list(filter(asset_filter, assets))
                if len(filtered_assets) != 1:
                    raise Exception("filtering assets returned more than one result")

                asset_href = filtered_assets[0]["href"]
                asset_response = requests.get(asset_href)
                if asset_response.status_code == 200:
                    zip_file = ZipFile(BytesIO(asset_response.content))
                    file_name = zip_file.namelist()[0]
                    file_path = zip_file.extract(member=file_name, path=tempfile.gettempdir())
                    file_paths.append(file_path)
                else:
                    raise Exception(f"requesting assets failed with HTTP error {asset_response.status_code}")
        else:
            raise Exception(f"requesting items failed with HTTP error {items_response.status_code}")
        return file_paths
