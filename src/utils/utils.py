import logging
import sys
from datetime import datetime
from pathlib import Path

from config.configuration import config


def setup_logger(log_file_name: str = None):
    logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(logging_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(config.logging_level)
    root_logger.addHandler(stream_handler)

    if log_file_name is not None:
        log_file_name = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        app_logs_path = "/logs/app"
        Path(app_logs_path).mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(f"{app_logs_path}/{log_file_name}.log")
        file_handler.setFormatter(logging.Formatter(logging_format))
        root_logger.addHandler(file_handler)


def get_output_path(generation_id):
    return f"/workspace/ifc_storage/{generation_id}.ifc"
