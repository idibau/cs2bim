import logging
import os
from datetime import datetime

from fastapi import FastAPI

from api.routes import router
from utils.utils import setup_logger

log_file_name = None
if os.getenv("ENVIRONMENT") == "development":
    log_file_name = f"app_{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}"
setup_logger(log_file_name)

logger = logging.getLogger(__name__)

logger.info("===================================================================")
logger.info("|                           Start API                             |")
logger.info("===================================================================")

app = FastAPI()
app.include_router(router)
