import logging
from loguru import logger
import sys

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, record.getMessage())
    
class NullLogger:
    def __init__(self,/, *args, **kwargs): pass
    def debug(self, /, *a, **kw): pass
    def info(self, /, *a, **kw): pass
    def warning(self, /, *a, **kw): pass
    def error(self, /, *a, **kw): pass
    def critical(self, /, *a, **kw): pass

default_null_logger = NullLogger()