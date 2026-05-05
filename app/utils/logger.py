import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance with a consistent format.

    Args:
        name: Logger name (pass __name__ from the calling module)

    Returns:
        logging.Logger: Configured logger writing to stdout
    """
    logger = logging.getLogger(name or "voice_assistant")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="[%(asctime)s] %(levelname)-8s %(name)s → %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
