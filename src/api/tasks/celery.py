import logging
import os
import sys
from pathlib import Path

from cs2bim.ifc.enum.ifc_version import IfcVersion
from utils import get_output_path
from celery import Celery
from cs2bim.model_generator import ModelGenerator
from config.configuration import config

logger = logging.getLogger(__name__)

celery_app = Celery(
    "cs2bim",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

celery_app.conf.task_track_started = True
celery_app.conf.result_expires = 3600


@celery_app.task(bind=True)
def model_generation_task(self, ifc_version, name, polygon, project_origin):
    try:
        root_logger = logging.getLogger()
        root_logger.setLevel(config.logging_level)
        logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(logging_format))

        env = os.getenv("ENVIRONMENT")
        if  env == "development":
            task_id = self.request.id
            task_logs_path = "/workspace/logs/tasks"
            Path(task_logs_path).mkdir(parents=True, exist_ok=True)
            log_file = f"{task_logs_path}/{task_id}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(logging_format))
            root_logger.addHandler(file_handler)

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
