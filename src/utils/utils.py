import logging
import sys
import yaml
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.configuration import config


def setup_logger(log_file_name: str):
    logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(logging_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(config.logging_level)
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


def get_output_path(generation_id: str) -> str:
    return f"/workspace/ifc/{generation_id}.ifc"


def load_yaml_as_flat_dict(path: str) -> dict:
    with open(path, "r") as f:
        yaml_data = yaml.safe_load(f)

    def flatten(data, parent_key=""):
        items = {}
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(flatten(value, new_key))
            else:
                items[new_key] = value
        return items

    return flatten(yaml_data)
