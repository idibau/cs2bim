import logging
import os
import sys
from datetime import datetime
from fastapi import FastAPI
from pathlib import Path

from api.routes import router
from config.configuration import config

logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(logging_format))

root_logger = logging.getLogger()
root_logger.setLevel(config.logging_level)
root_logger.addHandler(stream_handler)

env = os.getenv("ENVIRONMENT")
if env == "development":
    log_file_name = datetime.now().strftime("%Y-%m-%d--%H-%M-%S.log")
    app_logs_path = "/workspace/logs/app"
    Path(app_logs_path).mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(f"{app_logs_path}/{log_file_name}")
    file_handler.setFormatter(logging.Formatter(logging_format))
    root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

logger.info("===================================================================")
logger.info("|                           Start API                             |")
logger.info("===================================================================")

app = FastAPI()
app.include_router(router)
