# logging_config.py
import logging
import os


def setup_logger(name, log_file='logs/debug.log', level=logging.DEBUG):
    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
# $ ATP.views  # INFO - Checksheet opened successfully with data: 123331 - Module: ATP.views - Function: checksheet_data

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s # %(levelname)s $ %(name)s  - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
