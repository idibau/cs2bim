import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(log_file_name, logging_level):
    logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(logging_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    root_logger.addHandler(stream_handler)

    logs_path = "/workspace/logs"
    Path(logs_path).mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        f"{logs_path}/{log_file_name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(logging_format))

    root_logger.addHandler(file_handler)


def get_output_path(generation_id):
    return f"/workspace/ifc/{generation_id}.ifc"


def get_translation_key(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    value = value.strip("_")
    return value
