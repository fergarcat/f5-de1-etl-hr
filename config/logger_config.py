import logging
import os
from logging.handlers import RotatingFileHandler


# Ruta absoluta al directorio raíz del proyecto
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ruta absoluta a la carpeta de logs en la raíz del proyecto
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Ruta completa del archivo de log
LOG_FILE = os.path.join(LOG_DIR, "app.log")


logger = logging.getLogger(__name__)
#logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)


if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
