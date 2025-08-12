import argparse
import logging
import sys
from datetime import datetime

from config.configuration import config
from cs2bim.ifc.enum.ifc_version import IfcVersion
from cs2bim.model_generator import ModelGenerator

logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(logging_format))
log_file_name = datetime.now().strftime("%Y-%m-%d--%H-%M-%S.log")
file_handler = logging.FileHandler(f"output/{log_file_name}")
file_handler.setFormatter(logging.Formatter(logging_format))

root_logger = logging.getLogger()
root_logger.setLevel(config.logging_level)
root_logger.addHandler(stream_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

logger.info("===================================================================")
logger.info("|                         run locally                             |")
logger.info("===================================================================")

parser = argparse.ArgumentParser()

parser.add_argument("--MODE", choices=["cli", "api"], default="cli", help="Run mode: cli or api")
parser.add_argument("--IFC_VERSION", help="IFC version (e.g., IFC4)")
parser.add_argument("--NAME", help="Project name")
parser.add_argument("--POLYGON", help="Polygon")
parser.add_argument("--PROJECT_ORIGIN", help="Project origin 'x,y,z'")

args = parser.parse_args()

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
    ifc_file = model_generator.generate(ifc_version, args.NAME, args.POLYGON, project_origin)
    ifc_file.write(f"output/{args.NAME}.ifc")

