import logging
from loguru import logger
import sys
from pkms.logging import InterceptHandler

def setup_logging():
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.DEBUG)

    # optional: clean uvicorn default handlers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access","fastapi"):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG",
        backtrace=True,
        diagnose=True,
    )
