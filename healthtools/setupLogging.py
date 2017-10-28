import logging
import logging.config
from healthtools.config import LOGGING

def setup_logging(default_level=logging.INFO):
    """
    Setup logging configuration
    """
    try:
        logging.config.dictConfig(LOGGING)
    except Exception as ex:
        logging.basicConfig(level=default_level)
