import logging
import sys
from typing import Any

import yaml
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.configuration import config


def setup_logger(log_file_name: str):
    """
    Initializes the root logger that writes logs to both standard output and a rotating file.

    Args:
        log_file_name: The base name for the log file (without extension).
    """
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
    """
    Generate the output path for a generated IFC file.

    Args:
        generation_id: Unique identifier for the generation process.

    Returns:
        The absolute file path for the corresponding IFC file.
    """
    return f"/workspace/ifc/{generation_id}.ifc"


def load_yaml_as_flat_dict(path: str) -> dict[str, Any]:
    """
    Nested keys in the YAML file are flattened using dot notation. For example, a YAML structure like:

        database:
            host: localhost
            port: 5432

    becomes:

        {
            "database.host": "localhost",
            "database.port": 5432
        }

    Args:
        path: Path to the YAML configuration file.

    Returns:
        A flattened dictionary representation of the YAML file.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        yaml.YAMLError: If the YAML file contains invalid syntax.
    """
    with open(path, "r") as f:
        yaml_data = yaml.safe_load(f)

    def flatten(data, parent_key=""):
        items = {}
        if data is not None:
            for key, value in data.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    items.update(flatten(value, new_key))
                else:
                    items[new_key] = value
        return items

    return flatten(yaml_data)
