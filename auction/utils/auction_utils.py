import logging
from logging import Logger
from foundation.singleton import Singleton
import os

class log(metaclass=Singleton):

    def __init__(self, file_name="Default_Log"):
        """
        initialize the class with the logger name

        @param file_name file name for el logger file.
        """
        self.logger = None
        self.file_name = file_name

    def create_logger(name) -> Logger:
        """
        Creates a logger object with the format

        :param name: the name of the logger
        :return: the logger object with format and handler
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(base_dir + '/' + name + '.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[L:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                                      datefmt='%d-%m-%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def get_logger(self) -> Logger:
        """
        Gets the logger object with an specific format

        :return:
        """
        if self.logger is None:
            self.logger = self.create_logger(self.file_name)

        return self.logger