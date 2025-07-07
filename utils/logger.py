import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

logger = get_logger(__name__)