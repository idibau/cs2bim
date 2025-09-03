import logging
import tracemalloc

logger = logging.getLogger(__name__)


def start_measuring_memory_usage() -> None:
    tracemalloc.start()


def log_memory_usage() -> None:
    current_memory_usage = tracemalloc.get_traced_memory()[0] / 1000000
    peak_memory_usage = tracemalloc.get_traced_memory()[1] / 1000000
    logger.debug(f"Current Memory usage: {current_memory_usage}mb, Peak memory usage: {peak_memory_usage}mb")


def stop_measuring_memory_usage() -> None:
    tracemalloc.stop()
