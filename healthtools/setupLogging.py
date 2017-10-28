import os
import json
import logging.config

def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv('LOG_FILE', None)
    if value:
        path = value
    try:
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    except Exception as ex:
        logging.basicConfig(level=default_level)
