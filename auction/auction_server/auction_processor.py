from foundation.auction import Auction
from foundation.bidding_object import BiddingObject
from foundation.auction_process_object import AuctionProcessObject
from foundation.config import Config
from foundation.ipap_message_parser import IpapMessageParser
from foundation.module_loader import ModuleLoader
from foundation.auctioning_object import AuctioningObjectType
from foundation.field_def_manager import FieldDefManager

from datetime import datetime
from enum import Enum

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_field_key import IpapFieldKey
from foundation.module import Module

class AgentFieldSet(Enum):
    """
    States throughout which can pass the auctioning object.
    """
    SESSION_FIELD_SET_NAME = 0
    REQUEST_FIELD_SET_NAME = 1

class AuctionProcess(AuctionProcessObject):

    def __init__(self, key: str, module: Module, auction: Auction, config_dict: dict):
        super(AuctionProcess, self).__init__(key, module)
        self.config_dict = config_dict
        self.auction = auction
        self.bids = {}

    def insert_bid(self, bid: BiddingObject):
        if bid.get_key() not in self.bids:
            self.bids[bid.get_key()] = bid
        else:
            raise ValueError("Bid is already inserted in the AuctionProcess")

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

    def get_bids(self) -> dict:
        """
        Gets teh bids registered in the action process
        :return: dictionary with all bids
        """
        return self.bids


class AuctionProcessor(IpapMessageParser):
    """
    This class manages and executes algorithms for a set of auctions.

    Attributes
    ----------
    """

    def __init__(self, domain: int, module_directory: str):
        super(AuctionProcessor, self).__init__(domain)
        self.auctions = {}
        self.config = Config().get_config()
        self.field_sets = {}

        if not module_directory:
            if 'AUMProcessor' in self.config:
                if 'ModuleDir' in self.config['AUMProcessor']:
                    module_directory = self.config['AUMProcessor']['ModuleDir']
                else:
                    ValueError(
                        'Configuration file does not have {0} entry within {1}'.format('ModuleDir', 'AumProcessor'))
            else:
                ValueError('Configuration file does not have {0} entry,please include it'.format('AumProcessor'))

        if 'AUMProcessor' in self.config:
            if 'Modules' in self.config['AUMProcessor']:
                modules = self.config['AUMProcessor']['Modules']
                self.module_loader = ModuleLoader(module_directory, 'AUMProcessor', modules)
            else:
                ValueError(
                    'Configuration file does not have {0} entry within {1}'.format('Modules', 'AumProcessor'))
        else:
            ValueError('Configuration file does not have {0} entry,please include it'.format('AumProcessor'))

    def add_auction_process(self, auction: Auction):
        """
        adds a Auction to auction process list

        :param auction: auction to be added
        """
        try:
            key = auction.get_key()
            action = auction.get_action()
            module_name = action.name
            module = self.module_loader.get_module(module_name)
            action_process = AuctionProcess(key, module, action.get_config_params(), auction)
            module.init_module(action.get_config_params())
            self.auctions[key] = action_process
            return key
        except Exception as e:
            print('Error msg:', str(e))
            return None

    def execute_auction(self, key: str, start: datetime, end: datetime):
        """
        Executes the allocation algorithm for the auction
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        action_process = self.auctions[key]
        module = action_process.get_module()
        allocations = module.execute(key, start, end, action_process.get_bids())
        return allocations

    def add_bidding_object_to_auction_process(self, key: str, bidding_object: BiddingObject):
        """
        adds a bidding Object to auction process

        :param key: key of the auction process
        :param bidding_object: bidding object to add
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))
        action_process = self.auctions[key]

        if bidding_object.parent_auction.get_key() != action_process.key:
            raise ValueError("bidding object given {0} is not for the auction {1}".format(
                bidding_object.get_key(), key))

        if bidding_object.get_type() == AuctioningObjectType.BID:
            action_process.insert_bid(bidding_object)
        else:
            raise ValueError("bidding object is not BID type")

    def delete_bidding_object_from_auction_process(self, key: int, bidding_object: BiddingObject):
        """
        deletes a bidding Object from auction process

        :param key: key of the auction process
        :param bidding_object: bidding object to delete
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        action_process = self.auctions[key]
        action_process.bids.pop(bidding_object.get_key(), None)

    def delete_auction_process(self, key: str):
        """
        Deletes an auction process from the list.
        The caller must to remove all loop entries created for this process
        auction.
        :param key key of the auction process
        :return:
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        action_process = self.auctions.pop(key, None)
        if action_process:
            self.module_loader.release_module(action_process.get_module().get_module_name())

    def get_auction_process(self, key:str) -> AuctionProcess:
        """
        Gets the auction process with the key given
        :param key: key to find
        :return: auction process
        """
        if key not in self.auctions:
            raise ValueError("auction process with index:{0} was not found".format(key))

        return self.auctions.get(key)

    def get_session_information(self, message: IpapMessage):
        """
        gets the session information within the message.

        :param message message from where to extract the session information.
        :return: map of values that identify the session
        """
        pass

    def delete_auction(self, auction: Auction):
        """
        deletes an auction
        :param auction: auction to be deleted
        :return:
        """
        self.delete_auction_process(auction.get_key())

    def get_set_field(self, set_name: AgentFieldSet):
        if len(self.field_sets) == 0:
            field_def_manager = FieldDefManager()

            # Fill data auctions fields
            agent_session = set()
            agent_session.add(IpapFieldKey(field_def_manager.get_field('ipversion')['eno'],
                                           field_def_manager.get_field('ipversion')['ftype']))
            agent_session.add(IpapFieldKey(field_def_manager.get_field('srcip')['eno'],
                                           field_def_manager.get_field('srcip')['ftype']))
            agent_session.add(IpapFieldKey(field_def_manager.get_field('srcipv6')['eno'],
                                           field_def_manager.get_field('srcipv6')['ftype']))
            agent_session.add(IpapFieldKey(field_def_manager.get_field('srcport')['eno'],
                                           field_def_manager.get_field('srcport')['ftype']))
            self.field_sets[AgentFieldSet.SESSION_FIELD_SET_NAME] = agent_session

            # Fill option auctions fields
            agent_search_fields = set()
            agent_search_fields.add(IpapFieldKey(field_def_manager.get_field('start')['eno'],
                                           field_def_manager.get_field('start')['ftype']))
            agent_search_fields.add(IpapFieldKey(field_def_manager.get_field('stop')['eno'],
                                           field_def_manager.get_field('stop')['ftype']))
            agent_search_fields.add(IpapFieldKey(field_def_manager.get_field('resourceid')['eno'],
                                           field_def_manager.get_field('resourceid')['ftype']))
            self.field_sets[AgentFieldSet.REQUEST_FIELD_SET_NAME] = agent_search_fields

        return self.field_sets[set_name]
