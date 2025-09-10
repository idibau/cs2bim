import logging
from datetime import datetime
from fastapi import FastAPI

from api.routes import router
from config.configuration import Configuration
from utils.utils import setup_logger

config = Configuration.load("/workspace/config.yml")

setup_logger(f"api_{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}", config.logging_level)
logger = logging.getLogger(__name__)

logger.info("===================================================================")
logger.info("|                           Start API                             |")
logger.info("===================================================================")

app = FastAPI()
app.include_router(router)
