import os
import sys

from loguru import logger


def configure_logger() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.remove()
    is_prod = os.getenv("ENVIRONMENT", "development") == "production"
    logger.add(
        sys.stderr,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}" if not is_prod else "{message}",
        serialize=is_prod,
    )


configure_logger()
