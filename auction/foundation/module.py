from abc import ABCMeta
from abc import abstractmethod
from datetime import datetime


class Module(metaclass=ABCMeta):
    """
    this class represents the base class for auction processing modules
    """

    def __init__(self, module_name: str, file_name: str, own_name: str, module_handle):
        self.module_name = module_name
        self.file_name = file_name
        self.own_name = own_name
        self.lib_handle = module_handle
        self.refs = 0
        self.calls = 0

    @abstractmethod
    def init_module(self, config_param_list:dict):
        """
        Initialization method for starting modules.

        :param config_param_list: Configuration parameters list to
                                   be used on the module.
        """
        pass

    @abstractmethod
    def destroy_module(self):
        """
        Destroy method for ending modules.
        """
        pass

    @abstractmethod
    def execute(self, auction_key: str, start:datetime, stop:datetime, bids: dict) -> dict:
        """
        Executes the module (bidding process)

        :param auction_key: auction key
        :param start: start datetime
        :param stop: stop datetime
        :param bids: bids for the allocation process.
        :return:
        """
        pass

    @abstractmethod
    def execute_user(self, auctions: list, start:datetime, stop:datetime) -> list:
        """
        Execute the bidding process for the list of auctions given
        that are required to support a resource request interval.

        :param auctions:    auctions that must be executed.
        :param start: start datetime
        :param stop: stop datetime

        :return: bids created by the auction process.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reset flow data record for a rule

        :return:
        """
        pass

    def set_own_name(self, own_name:str):
        """
        Sets own name
        :param own_name: own name
        """
        self.own_name=own_name

    def link(self):
        """
        increases module reference counter
        """
        self.refs = self.refs + 1

    def unlink(self):
        """
        decreases module reference counter
        """
        self.refs = self.refs - 1

    def get_module_handle(self):
        """
        Gets the module handle
        :return:
        """
        return self.lib_handle

    def get_module_name(self) -> str:
        """
        Gets module name
        :return:
        """
        return self.module_name

    def get_file_name(self) -> str:
        """
        Gets the file name from where the module was loaded
        :return:
        """
        return self.file_name

    def get_own_name(self) -> str:
        """
        Gets the own name
        :return:
        """
        return self.own_name

    def get_references(self) -> int:
        """
        Gets teh reference count
        :return:
        """
        return self.refs
