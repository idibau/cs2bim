import tracemalloc

def start_measuring_memory_usage() -> None:
    tracemalloc.start()

def log_memory_usage() -> None:
    logger.debug(
        f"Current Memory usage: {tracemalloc.get_traced_memory()[0] / 1000000}mb, Peak memory usage: {tracemalloc.get_traced_memory()[1] / 1000000}mb"
    )

def stop_measuring_memory_usage() -> None:
    tracemalloc.stop()