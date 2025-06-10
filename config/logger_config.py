# logger_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

# Create log directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# General logger configuration

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log message format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# File handler with rotation
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=3)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.propagate = False
