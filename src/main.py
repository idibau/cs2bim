import sys
import logging

from tin2ifc.ifc_config import IfcConfig
from tin2ifc.ifc_writer import IfcWriter
from tin2ifc.geometry_representaion import GeometryRepresentaion
from tin2ifc.triangulation import Triangulation

logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(logging_format))

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    config = IfcConfig()
    config.origin = (2689046.0, 1285092.0, 470.61)
    config.origin_shift = (2689046.0, 1285092.0, 470.61)
    config.geometry_representation = GeometryRepresentaion.TESSELLATION

    ifc = IfcWriter("test", config)
    
    triangulation1 = Triangulation()
    triangulation1.load_from_stl(f"files/poly_1.stl")
    ifc.add_parcel(triangulation1)
    triangulation2 = Triangulation()
    triangulation2.load_from_stl(f"files/poly_2.stl")
    ifc.add_parcel(triangulation2)
    triangulation3 = Triangulation()
    triangulation3.load_from_stl(f"files/poly_3.stl")
    ifc.add_parcel(triangulation3)
    triangulation4 = Triangulation()
    triangulation4.load_from_stl(f"files/poly_4.stl")
    ifc.add_parcel(triangulation4)
    
    ifc.build()

    ifc.write(f"files/merged_tess_georef50.ifc")