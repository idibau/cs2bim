"""
Celery worker module

Celery worker configuration and task for IFC model generation from geospatial data.
Handles task queue setup, logging initialization, and model generation processes.
"""

import logging
from celery import Celery
from celery.signals import worker_process_init
from core.ifc.model.coordinate import Coordinates
from datetime import datetime

from config.configuration import config
from core.ifc.model.ifc_version import IfcVersion
from core.model_generator import ModelGenerator
from i18n.language import Language
from utils.utils import get_output_path, setup_logger

app = Celery(
    "cs2bim",
    broker=f"redis://{config.redis.host}:{config.redis.port}/{config.redis.db.celery_broker}",
    backend=f"redis://{config.redis.host}:{config.redis.port}/{config.redis.db.celery_backend}"
)

app.conf.task_track_started = True
app.conf.result_expires = 86400
if config.redis.global_keyprefix:
    app.conf.result_backend_transport_options = {
        "global_keyprefix": config.redis.global_keyprefix
    }
if config.redis.queue:
    app.conf.task_default_queue = config.redis.queue


@worker_process_init.connect
def setup_logger_on_worker(**kwargs):
    """Initialize worker-specific logger on worker startup."""
    setup_logger(f"worker_{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}")


@app.task(bind=True)
def model_generation_task(self, ifc_version: str, name: str, polygon: str, project_origin: list[float],
                          language: str | None):
    """
    Generate IFC model from geospatial data.

    Args:
        ifc_version: Target IFC schema version
        name: Project name
        polygon: polygon as a wkt string
        project_origin: Coordinates for project origin
        language: Optional language

    Returns:
        Path to generated IFC file

    Raises:
        Exception: If model generation fails for any reason.
    """
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"task {self.request.id}: Starting model generation")
        model_generator = ModelGenerator()
        project_origin = Coordinates(*project_origin) if project_origin else None
        model = model_generator.generate(IfcVersion(ifc_version), name, polygon, project_origin)
        language = Language(language) if language else None
        ifc_file = model.map_to_ifc(language)
        output_path = get_output_path(self.request.id)
        ifc_file.write(output_path)
        logger.info(f"task {self.request.id}: Model generation completed, file saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"task {self.request.id}: Model generation failed: {str(e)}", exc_info=True)
        raise
