import logging
import os

from celery import Celery

from core.ifc.enum.ifc_version import IfcVersion
from core.model_generator import ModelGenerator
from utils.utils import get_output_path, setup_logger

app = Celery(
    "cs2bim",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

app.conf.task_track_started = True
app.conf.result_expires = 86400


@app.task(bind=True)
def model_generation_task(self, ifc_version, name, polygon, project_origin):
    log_file_name = None
    if os.getenv("ENVIRONMENT") == "development":
        log_file_name = f"task_{self.request.id}"
    setup_logger(log_file_name)

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Task {self.request.id}: Starting model generation")
        model_generator = ModelGenerator()
        ifc_file = model_generator.generate(IfcVersion(ifc_version), name, polygon, project_origin)
        output_path = get_output_path(self.request.id)
        ifc_file.write(output_path)
        logger.info(f"Task {self.request.id}: Model generation completed, file saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Task {self.request.id}: Model generation failed: {str(e)}")
        raise
