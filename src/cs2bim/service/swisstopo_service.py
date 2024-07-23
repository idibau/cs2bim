import requests
import tempfile
from typing import Any
from io import BytesIO
from zipfile import ZipFile

from cs2bim.bounding_box import BoundingBox

class SwisstopoService:

    def __init__(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def fetch_dtm_files(self, bounding_box: BoundingBox) -> list[str]:
        file_paths = []
        items_url = "https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d/items"
        items_response = requests.get(items_url, params={"bbox": bounding_box.get_wgs84_bounding_box_as_string()})
        if items_response.status_code == 200:
            for feature in items_response.json()["features"]:
                assets = feature["assets"].values()
                filtered_assets = list(filter(self.asset_filter, assets))
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

    def asset_filter(self, asset: Any):
        return asset["type"] == "application/x.ascii-xyz+zip" and asset["eo:gsd"] == 0.5