import logging
from logging import Logger
from foundation.config import Config
import os


def get_logger(name) -> Logger:
    """
    Creates a logger object with the format
    :param name: the name of the logger
    :return: the logger object with format and handler
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(base_dir + '/'  + name + '.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[L:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                                  datefmt = '%d-%m-%Y %H:%M:%S')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
