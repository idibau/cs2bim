import logging
from datetime import datetime
from fastapi import FastAPI

from api.routes import router
from utils.utils import setup_logger

setup_logger(f"api_{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}")
logger = logging.getLogger(__name__)

logger.info("===================================================================")
logger.info("|                           Start API                             |")
logger.info("===================================================================")

app = FastAPI()
app.include_router(router)
