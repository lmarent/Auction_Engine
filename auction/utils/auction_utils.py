import logging
from logging import Logger
from foundation.singleton import Singleton
import os
from datetime import datetime

class log(metaclass=Singleton):

    def __init__(self, file_name="Default_Log"):
        """
        initialize the class with the logger name

        @param file_name file name for el logger file.
        """
        self.logger = None
        self.file_name = file_name

    def create_logger(self):
        """
        Creates a logger object with the format

        :return: the logger object with format and handler
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger = logging.getLogger(self.file_name)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(base_dir + '/' + self.file_name + '.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[L:%(filename)s - %(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                                      datefmt='%d-%m-%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        self.logger = logger

    def get_logger(self) -> Logger:
        """
        Gets the logger object with an specific format

        :return:
        """
        if self.logger is None:
            self.create_logger()

        return self.logger

class DateUtils(metaclass=Singleton):
    """
    Utils for date operations.
    """

    @staticmethod
    def calculate_when(start: datetime) -> float:
        """
        Calculates the datetime of an event given the current loop time
        :param start: datetime when the event should start
        :return: time in milliseconds when we should start the new event
        """
        if start <= datetime.now():
            return 0
        else:
            return (start - datetime.now()).total_seconds()
