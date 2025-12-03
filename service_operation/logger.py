import logging
from pythonjsonlogger import jsonlogger
import os

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger():
    """Create and return a JSON structured logger for the API."""
    # Create logger
    logger = logging.getLogger('my_api_logger')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt='%(levelname)s %(name)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for errors
    error_filepath = os.path.join(LOG_DIR, 'error.log')
    error_file_handler = logging.FileHandler(error_filepath)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)

    # Optional: file handler for all logs
    all_filepath = os.path.join(LOG_DIR, 'app.log')
    all_file_handler = logging.FileHandler(all_filepath)
    all_file_handler.setLevel(logging.INFO)
    all_file_handler.setFormatter(formatter)
    logger.addHandler(all_file_handler)

    return logger

# Initialize logger instance
API_LOGGER = setup_logger()
