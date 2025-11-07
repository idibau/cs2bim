"""
Run Script for IFC Model Generation

This script is a command-line utility for generating IFC models using the specified parameters such as
IFC version, project name, polygon, and optional project origin and language.

Example:
    Run the script from the command line:

        python main.py \
          --IFC_VERSION=<version> \
          --NAME=<name> \
          --POLYGON=<polygon> \
          --PROJECT_ORIGIN=<origin>
          --LANGUAGE=<langugae>

Required Arguments:
    --IFC_VERSION (str): The IFC version (e.g., "IFC4").
    --NAME (str): The name of the project.
    --POLYGON (str): Polygon data for the model geometry.

Optional Arguments:
    --PROJECT_ORIGIN (str): Comma-separated XYZ coordinates for project origin
        (e.g., "0.0,0.0,0.0"). If omitted, a calculated origin is used.
    --LANGUAGE (str): Language code for localization (e.g., "EN").
"""

import argparse
import logging
import sys

from core.ifc.model.coordinates import Coordinates
from core.ifc.model.ifc_version import IfcVersion
from core.model_generator import ModelGenerator
from i18n.language import Language
from utils.memory_logger import start_measuring_memory_usage, log_memory_usage, stop_measuring_memory_usage
from utils.utils import setup_logger, get_output_path

# ---------------------------------------------------------------------------
# Setup and Initialization
# ---------------------------------------------------------------------------

setup_logger("script")
logger = logging.getLogger(__name__)

logger.info("===================================================================")
logger.info("|                         Run Script                              |")
logger.info("===================================================================")

# ---------------------------------------------------------------------------
# Argument Parser Configuration
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Generate an IFC model based on provided parameters.")
parser.add_argument("--IFC_VERSION", help="IFC version (e.g., IFC4)")
parser.add_argument("--NAME", help="Project name")
parser.add_argument("--POLYGON", help="Polygon data for the IFC model")
parser.add_argument("--PROJECT_ORIGIN", help="Project origin as 'x,y,z'")
parser.add_argument("--LANGUAGE", help="Language code (optional)")

args = parser.parse_args()

# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

start_measuring_memory_usage()

if not (args.IFC_VERSION and args.NAME and args.POLYGON):
    print("Missing required parameters for CLI mode", file=sys.stderr)
    parser.print_help()
else:
    ifc_version = IfcVersion(args.IFC_VERSION)

    # -----------------------------------------------------------------------
    # Parse and Validate Project Origin
    # -----------------------------------------------------------------------
    if args.PROJECT_ORIGIN:
        try:
            origin_values = [float(coord.strip()) for coord in args.PROJECT_ORIGIN.split(",")]
        except ValueError:
            raise ValueError(
                "PROJECT_ORIGIN must contain only numbers in the format 'float,float,float' (e.g., 0.0,0.0,0.0)."
            )
        if len(origin_values) != 3:
            raise ValueError(
                "PROJECT_ORIGIN must contain exactly three values separated by commas (e.g., 0.0,0.0,0.0)."
            )
        project_origin = Coordinates(*origin_values)
    else:
        project_origin = None

    language = Language(args.LANGUAGE) if args.LANGUAGE else None

    logger.info(
        f"IFC_VERSION: {ifc_version.name}, NAME: {args.NAME}, POLYGON: {args.POLYGON}, "
        f"PROJECT_ORIGIN: {project_origin if project_origin else 'calculated'}, LANGUAGE: {language}"
    )

    # -----------------------------------------------------------------------
    # Model Generation and IFC Mapping
    # -----------------------------------------------------------------------
    model_generator = ModelGenerator()

    log_memory_usage()

    model = model_generator.generate(ifc_version, args.NAME, args.POLYGON, project_origin)
    ifc_file = model.map_to_ifc(language)
    ifc_file.write(get_output_path(args.NAME))

    log_memory_usage()
    stop_measuring_memory_usage()
