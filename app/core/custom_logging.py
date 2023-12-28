import logging
import sys

from loguru import logger


def configure_logger():
    """
    Configure Loguru logger.
    Override Uvicorn/FastAPI logger:
    https://medium.com/1mgofficial/how-to-override-uvicorn-logger-in-fastapi-using-loguru-124133cdcd4e
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<level>{level: <8}</level>"
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>  "
        "|  <level>{message}</level>"
        "   (<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>)",
    )

    # logger.level("INFO", color="<green>")

    # logging.basicConfig(handlers=[InterceptHandler()], level=0)
    # logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    # for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
    #     _logger = logging.getLogger(_log)
    #     _logger.handlers = [InterceptHandler()]

    # logger.bind(request_id=None, method=None)

    return logger


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id="app")
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
