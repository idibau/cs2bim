import logging
import os
from celery import Celery, signals
from celery.signals import worker_process_init

from datetime import datetime
from core.ifc.model.ifc_version import IfcVersion
from core.model_generator import ModelGenerator
from i18n.language import Language
from utils.utils import get_output_path, setup_logger
from config.configuration import config

app = Celery(
    "cs2bim",
    broker=f"redis://{config.redis.host}:{config.redis.port}/{config.redis.db.celery_broker}",
    backend=f"redis://{config.redis.host}:{config.redis.port}/{config.redis.db.celery_backend}"
)

app.conf.task_track_started = True
app.conf.result_expires = 86400


@worker_process_init.connect
def setup_logger_on_worker(**kwargs):
    setup_logger(f"worker_{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}")


@app.task(bind=True)
def model_generation_task(self, ifc_version, name, polygon, project_origin, language):
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Task {self.request.id}: Starting model generation")
        model_generator = ModelGenerator()
        model = model_generator.generate(IfcVersion(ifc_version), name, polygon, project_origin)
        language = Language(language) if language else None
        ifc_file = model.map_to_ifc(language)
        output_path = get_output_path(self.request.id)
        ifc_file.write(output_path)
        logger.info(f"Task {self.request.id}: Model generation completed, file saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Task {self.request.id}: Model generation failed: {str(e)}", exc_info=True)
        raise
