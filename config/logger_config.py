import logging
import os
from logging.handlers import RotatingFileHandler
import colorlog


# Ruta absoluta al directorio
PROJECT_ROOT = os.environ.get("PROJECT_ROOT", "/tmp")
print(f"Project root: {PROJECT_ROOT}")

# Ruta absoluta a la carpeta de logs
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Archivos de log por componente
LOG_FILES = {
    'main': os.path.join(LOG_DIR, "etl_main.log"),
    'kafka': os.path.join(LOG_DIR, "kafka_consumer.log"),
    'mongodb': os.path.join(LOG_DIR, "mongodb.log"),
    'sql': os.path.join(LOG_DIR, "sql_db.log"),
    'transform': os.path.join(LOG_DIR, "data_transform.log")
}


def setup_etl_logger(name='etl_main', level=logging.INFO, log_to_file=True):
    """
    Configura logger específico para componentes ETL
    
    Args:
        name (str): Nombre del componente (kafka, mongodb, sql, transform, main)
        level: Nivel de logging
        log_to_file (bool): Si debe escribir a archivo específico
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar reconfigurar loggers existentes
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formatter para archivos 
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formatter para consola (más limpio)
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Handler para archivo
    if log_to_file:
        log_file = LOG_FILES.get(name, LOG_FILES['main'])
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Handler consola
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Evitar propagación para evitar duplicados
    logger.propagate = False
    
    return logger


# Loggers para cada componente del ETL
kafka_logger = setup_etl_logger('kafka_consumer', logging.INFO)
mongodb_logger = setup_etl_logger('mongodb', logging.INFO)
sql_logger = setup_etl_logger('sql_database', logging.INFO)
transform_logger = setup_etl_logger('data_transform', logging.INFO)
main_logger = setup_etl_logger('etl_main', logging.INFO)

# Logger general (backward compatibility)
logger = main_logger


def get_component_logger(component_name):
    """
    Obtiene logger específico para un componente
    
    Args:
        component_name (str): 'kafka', 'mongodb', 'sql', 'transform', 'main'
    
    Returns:
        logging.Logger: Logger del componente
    """
    loggers = {
        'kafka': kafka_logger,
        'mongodb': mongodb_logger,
        'sql': sql_logger,
        'transform': transform_logger,
        'main': main_logger
    }
    return loggers.get(component_name, main_logger)


def log_data_processing(logger, operation, record_count=None, success=True):
    """
    Helper function para logging consistente de operaciones ETL
    
    Args:
        logger: Logger a usar
        operation (str): Descripción de la operación
        record_count (int): Número de registros procesados
        success (bool): Si la operación fue exitosa
    """
    if success:
        if record_count:
            logger.info(f"✓ {operation} - {record_count} registros procesados")
        else:
            logger.info(f"✓ {operation} - Completado")
    else:
        if record_count:
            logger.error(f"✗ {operation} - Error procesando {record_count} registros")
        else:
            logger.error(f"✗ {operation} - Error")


# Ejemplo de uso:
# kafka_logger.info("Conectando a Kafka...")
# log_data_processing(transform_logger, "Transformación de datos personales", 150, True)
# mongodb_logger.error("Error al insertar documento")