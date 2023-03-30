import logging
import os

def setup_logger(log_file='console.log', log_level=logging.INFO, console_level=logging.WARNING):
    logger = logging.getLogger()
    logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s [%(filename)s] [%(levelname)s] %(message)s')

    # Log to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)  # Set log level for file handler
    logger.addHandler(file_handler)

    # Log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)  # Set log level for console handler
    logger.addHandler(console_handler)

    return logger


if not os.path.exists('logs'):
    os.makedirs('logs')

logger = setup_logger(log_file='logs/console.log')
