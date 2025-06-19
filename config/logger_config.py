"""
Logger Configuration for DataTech Solutions ETL System
"""
import logging
import colorlog

def setup_logger(name="DataTechSolutions", level=logging.INFO):
    """Setup colorized logger for DataTech Solutions"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler with color formatting
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(level)
    
    # Color formatter
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Default logger instance
logger = setup_logger()
