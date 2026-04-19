import logging
import os
from logging.handlers import RotatingFileHandler
from src.core.config import Config

def setup_logging(name="mood-music-hub"):
    """
    Sets up a standardized logger with both console and file output.
    Uses RotatingFileHandler to prevent log files from growing indefinitely.
    """
    # Use config for directories
    log_dir = Config.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'application.log')
    
    # Configure formatting
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Console Handler (Stdout)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    return logger
