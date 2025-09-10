import logging
from datetime import datetime

from celery import Celery
from celery.signals import worker_process_init

from config.configuration import Configuration
from core.ifc.model.ifc_version import IfcVersion
from core.model_generator import ModelGenerator
from utils.utils import get_output_path, setup_logger

app = Celery(
    "cs2bim",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

app.conf.task_track_started = True
app.conf.result_expires = 86400

config = None


@worker_process_init.connect
def setup_logger_on_worker(**kwargs):
    global config
    config = Configuration.load("/workspace/config.yml")
    setup_logger(f"worker_{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}", config.logging_level)


@app.task(bind=True)
def model_generation_task(self, ifc_version, name, polygon, project_origin):
    global config
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Task {self.request.id}: Starting model generation")
        model_generator = ModelGenerator()
        model = model_generator.generate(config, IfcVersion(ifc_version), name, polygon, project_origin)
        ifc_file = model.map_to_ifc()
        output_path = get_output_path(self.request.id)
        ifc_file.write(output_path)
        logger.info(f"Task {self.request.id}: Model generation completed, file saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Task {self.request.id}: Model generation failed: {str(e)}", exc_info=True)
        raise
