import argparse
import logging
import sys

from core.ifc.model.coordinates import Coordinates
from core.ifc.model.ifc_version import IfcVersion
from core.model_generator import ModelGenerator
from i18n.language import Language
from utils.memory_logger import start_measuring_memory_usage, log_memory_usage, stop_measuring_memory_usage
from utils.utils import setup_logger, get_output_path

setup_logger("script")

logger = logging.getLogger(__name__)

logger.info("===================================================================")
logger.info("|                         Run Script                              |")
logger.info("===================================================================")

parser = argparse.ArgumentParser()

parser.add_argument("--IFC_VERSION", help="IFC version (e.g., IFC4)")
parser.add_argument("--NAME", help="Project name")
parser.add_argument("--POLYGON", help="Polygon")
parser.add_argument("--PROJECT_ORIGIN", help="Project origin 'x,y,z'")
parser.add_argument("--LANGUAGE", help="Language")

args = parser.parse_args()

start_measuring_memory_usage()

if not (args.IFC_VERSION and args.NAME and args.POLYGON):
    print("Missing required parameters for CLI mode", file=sys.stderr)
    parser.print_help()
else:
    ifc_version = IfcVersion(args.IFC_VERSION)
    if args.PROJECT_ORIGIN:
        try:
            origin_values = [float(coord.strip()) for coord in args.PROJECT_ORIGIN.split(",")]
        except ValueError:
            raise ValueError(
                "PROJECT_ORIGIN must contain only numbers in the format 'float,float,float' (e.g., 0.0,0.0,0.0).")
        if len(origin_values) != 3:
            raise ValueError(
                "PROJECT_ORIGIN must contain exactly three values separated by commas (e.g., 0.0,0.0,0.0).")
        project_origin = Coordinates(*origin_values)
    else:
        project_origin = None

    language = Language(args.LANGUAGE) if args.LANGUAGE else None
    logger.info(
        f"IFC_VERSION: {ifc_version.name}, NAME: {args.NAME}, POLYGON: {args.POLYGON}, PROJECT_ORIGIN: {project_origin if not project_origin is None else 'calculated'}, LANGUAGE: {language}"
    )
    model_generator = ModelGenerator()
    log_memory_usage()
    model = model_generator.generate(ifc_version, args.NAME, args.POLYGON, project_origin)
    ifc_file = model.map_to_ifc(language)
    ifc_file.write(get_output_path(args.NAME))
    log_memory_usage()

    stop_measuring_memory_usage()
