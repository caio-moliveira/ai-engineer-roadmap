import logging
import sys

MAIN_LOGGER_NAME = 'main_logger'

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logger(name: str = MAIN_LOGGER_NAME, log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    # Evita duplicar handlers se já configurado
    if logger.handlers:
        return logger  

    logger.setLevel(log_level)
    logger.propagate = False

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter())

    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
