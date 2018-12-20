from foundation.config import Config
from foundation.auction import Auction
from foundation.module import Module
from foundation.auction_process_object import AuctionProcessObject
from foundation.module_loader import ModuleLoader
from foundation.id_source import IdSource

from datetime import datetime


class RequestProcess(AuctionProcessObject):

    def __init__(self, key: str, session_id: str, module: Module, auction: Auction, config_dict: dict, start: datetime,
                 stop: datetime):
        super(RequestProcess, self).__init__(key, module)
        self.config_dict = config_dict
        self.start = start
        self.stop = stop
        self.session_id = session_id
        self.auctions = {}
        self.insert_auction(auction)

    def insert_auction(self, auction: Auction):
        if auction.get_key() not in self.auctions:
            self.auctions[auction.get_key()] = auction
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

    def set_session_id(self, session_id: str):
        """
        Sets the session id for the request

        :param session_id: session identifier
        :return:
        """
        self.session_id = session_id

    def get_session_id(self) -> str:
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

    def add_request(self, session_id: str, config_dic: dict, auction: Auction, start: datetime, stop: datetime):
        """
        Adds a new request to the list of request to execute.

        :param session_id: session Id to be used
        :param config_dic: configuration parameters for the process
        :param auction: auction to be used
        :param start: start date time
        :param stop: end date time
        :return:
        """
        module_name = auction.get_action().get_name() + "user"
        module = self.module_loader.get_module(module_name)
        module.init_module(config_dic)
        key = str(IdSource().new_id())
        request_process = RequestProcess(key, session_id, module, auction, config_dic, start, stop)
        self.requests[key] = request_process

    def delete_request(self, key: str):
        """
        Deletes a request from the list of request to execute.

        :param key:
        :return:
        """
        if key not in self.requests:
            raise ValueError("Request key:{0} was not found".format(key))

        request_process = self.requests.pop(key)
        self.module_loader.release_module(request_process.get_module().get_module_name())
        IdSource().free_id(int(request_process.get_key()))

    def release_request(self, key: str):
        """
        Releases the module attached to the request

        :param key:
        :return:
        """
        if key not in self.requests:
            raise ValueError("Request key:{0} was not found".format(key))

        request_process = self.requests[key]
        self.module_loader.release_module(request_process.get_module().get_module_name())

    def execute_request(self, key: str):
        """
        Executes the algorithm attached to the request.

        :param key: request process key to execute.
        :return: new bid created.
        """
        if key not in self.requests:
            raise ValueError("Request key:{0} was not found".format(key))

        request_process = self.requests[key]
        module = request_process.get_module()
        bids = module.execute_user(request_process.get_auctions(),
                                   request_process.get_start(), request_process.get_stop())
        return bids

    def add_auction_request(self, key: str, auction: Auction):
        """
        Adds an auction to auction list in the request.

        :param key: request process key where the auction is going to be added
        :param auction: auction to add
        :return:
        """
        if key not in self.requests:
            raise ValueError("Request key:{0} was not found".format(key))

        request_process = self.requests[key]

        # Second, look for the auction in the list of auction already inserted, if it exists generates an error
        if auction.get_key() in request_process.auctions:
            raise ValueError("Auction key:{0} is already inserted in the request process {1}".format(
                auction.get_key(), key))

        # Searches for the module name on those already loaded.
        module_name = auction.get_action().get_name() + "user"
        if module_name == request_process.get_module().get_module_name():
            request_process.auctions[auction.get_key()] = auction
        else:
            raise ValueError("the module loaded {0} must be the same {1} for request {2}".format(
                module_name, request_process.get_module().get_module_name(), key
            ))

    def delete_auction_request(self, key: str, auction: Auction):
        """
        Deletes an auction to auction list in the request.

        :param key: request process key where the auction is going to be deletec
        :param auction: auction to delete
        :return:
        """
        if key not in self.requests:
            raise ValueError("Request key:{0} was not found".format(key))

        request_process = self.requests[key]
        if auction.get_key() not in request_process.auctions:
            raise ValueError("Auction with key:{0} was not found in request process with key".format(
                auction.get_key().key))
        else:
            request_process.auctions.pop(auction.get_key())

    def get_session_for_request(self, key: str) -> str:
        """
        Gets the sessionId generating a request process

        :param key: request process key
        :return:
        """
        if key not in self.requests:
            raise ValueError("Request key:{0} was not found".format(key))

        request_process = self.requests[key]
        return request_process.get_session_id()

    @staticmethod
    def get_config_group() -> str:
        """
        Gets the config group for the agent.

        :return:
        """
        return "AGNTProcessor"
