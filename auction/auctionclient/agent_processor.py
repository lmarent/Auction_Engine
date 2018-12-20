from foundation.config import Config
from foundation.auction import Auction
from foundation.module import Module
from foundation.auction_process_object import AuctionProcessObject
from foundation.module_loader import ModuleLoader
from foundation.id_source import IdSource

from datetime import datetime

class RequestProcess(AuctionProcessObject):

    def __init__(self, key: str, module: Module, auction: Auction, config_dict: dict, start:datetime, stop:datetime):
        super(RequestProcess, self).__init__(key, module)
        self.config_dict = config_dict
        self.start = start
        self.stop = stop
        self.session_id = None
        self.auctions = {}

    def insert_auction(self, auction: Auction):
        if auction.get_key() not in self.auctions:
            self.auction[auction.get_key()] = auction
        else:
            raise ValueError("Auction is already inserted in the RequestProcess")

    def get_module(self) -> Module:
        """
        Gets the module associated with the auction process

        :return: Module
        """
        return self.module

    def get_config_params(self) -> dict:
        """
        Gets config params
        :return:
        """
        return self.config_dict

    def set_session_id(self,session_id:str):
        """
        Sets the session id for the request

        :param session_id: session identifier
        :return:
        """
        self.session_id = session_id

    def get_session_id(self)-> str:
        """
        Gets the session id being used by the request
        :return: session id string
        """
        return self.session_id

    def get_start(self) -> datetime:
        """
        Gets start time
        :return:
        """
        return self.start

    def get_stop(self) -> datetime:
        """
        Gets stop time
        :return:
        """
        return self.stop

    def get_auctions(self) -> dict:
        """
        Gets the auctions registered in the request process
        :return: dictionary with all auctions
        """
        return self.auctions


class AgentProcessor:

    def __init__(self, domain: int, module_directory: str):
        self.domain = domain
        self.requests = {}
        self.config = Config().get_config()
        self.field_sets = {}

        if not module_directory:
            if 'AGNTProcessor' in self.config:
                if 'ModuleDir' in self.config['AGNTProcessor']:
                    module_directory = self.config['AGNTProcessor']['ModuleDir']
                else:
                    ValueError(
                        'Configuration file does not have {0} entry within {1}'.format('ModuleDir', 'AGNTProcessor'))
            else:
                ValueError('Configuration file does not have {0} entry,please include it'.format('AGNTProcessor'))

        if 'AGNTProcessor' in self.config:
            if 'Modules' in self.config['AGNTProcessor']:
                modules = self.config['AGNTProcessor']['Modules']
                self.module_loader = ModuleLoader(module_directory, 'AGNTProcessor', modules)
            else:
                ValueError(
                    'Configuration file does not have {0} entry within {1}'.format('Modules', 'AGNTProcessor'))
        else:
            ValueError('Configuration file does not have {0} entry,please include it'.format('AGNTProcessor'))

    def add_request(self, session_id:str, config_dic: dict, auction:Auction, start:datetime, stop:datetime):
        """
        Adds a new request to the list of request to execute.

        :param session_id:
        :param params:
        :param auction:
        :param start:
        :param stop:
        :return:
        """
        module_name = auction.get_module_name() + "user"
        module = self.module_loader.get_module(module_name)
        key =
        RequestProcess(key: str, module, auction, config_dict, start, stop)


    def delete_request(self, key:str):
        """
        Deletes a request from the list of request to execute.

        :param key:
        :return:
        """

    def release_request(self, key:str):
        """
        Releases the module attached to the request

        :param key:
        :return:
        """

    def execute_request(self, key:str):
        """
        Executes the algorithm attached to the request.

        :param key:
        :return:
        """

    def add_auction_request(self, key:str, auction:Auction):
        """
        Adds an auction to auction list in the request.

        :param key:
        :param auction:
        :return:
        """

    def delete_auction_request(self, key:str, auction:Auction):
        """
        Deletes an auction to auction list in the request.

        :param key:
        :param auction:
        :return:
        """

    def get_session_for_request(self, key:str):
        """
        Gets the sessionId generating a request process

        :param key:
        :return:
        """

    def get_config_group(self) -> str:
        """
        Gets the config group for the agent.

        :return:
        """
        return "AGNTProcessor"