import argparse
import logging
import sys

from core.ifc.model.ifc_version import IfcVersion
from core.model_generator import ModelGenerator
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

args = parser.parse_args()

start_measuring_memory_usage()

if not (args.IFC_VERSION and args.NAME and args.POLYGON):
    print("Missing required parameters for CLI mode", file=sys.stderr)
    parser.print_help()
else:
    ifc_version = IfcVersion(args.IFC_VERSION)
    project_origin = None
    if args.PROJECT_ORIGIN:
        try:
            project_origin = tuple(map(float, args.PROJECT_ORIGIN.split(",")))
        except:
            raise ValueError("PROJECT_ORIGIN must be in format float,float,float")

    logger.info(
        f"IFC_VERSION: {ifc_version.name}, NAME: {args.NAME}, POLYGON: {args.POLYGON}, PROJECT_ORIGIN: {project_origin if not project_origin is None else 'calculated'}"
    )
    model_generator = ModelGenerator()
    log_memory_usage()
    ifc_file = model_generator.generate(ifc_version, args.NAME, args.POLYGON, project_origin)
    ifc_file.write(get_output_path(args.NAME))
    log_memory_usage()

    stop_measuring_memory_usage()
