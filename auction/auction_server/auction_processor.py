
from foundation.auction import Auction
from foundation.bidding_object import BiddingObject
from foundation.auction_process_object import AuctionProcessObject
from foundation.config import Config
from foundation.ipap_message_parser import IpapMessageParser

from datetime import datetime
from python_wrapper.ipap_message import IpapMessage

class AuctionProcess(AuctionProcessObject):

    def __init__(self, auction: Auction, config_dict: dict):
        super(AuctionProcess, self).__init__()
        self.config_dict = config_dict
        self.bids = {}

    def insert_bid(self, bid : BiddingObject):
        if bid.get_key() not in self.bids:
            self.bids[bid.get_key()] = bid
        else:
            raise ValueError("Bid is already inserted in the AuctionProcess")


class AuctionProcessor(IpapMessageParser):
    """
    This class manages and executes algorithms for a set of auctions.

    Attributes
    ----------
    """

    def __init__(self, domain:int, module_directory:str):
        super(AuctionProcessor,self).__init__(domain)
        self.auctions = {}
        self.config = Config().get_config()

        if not module_directory:
            if 'AumProcessor' in self.config:
                if 'ModuleDir' in self.config['AumProcessor']:
                    module_directory = self.config['AumProcessor']['ModuleDir']
                else:
                    ValueError('Configuration file does not have {0} entry within {1}'.format('ModuleDir', 'AumProcessor'))
            else:
                ValueError('Configuration file does not have {0} entry,please include it'.format('AumProcessor'))

        if 'AumProcessor' in self.config:
            if 'Modules' in self.config['AumProcessor']:
                module_directory = self.config['AumProcessor']['Modules']
            else:
                ValueError(
                    'Configuration file does not have {0} entry within {1}'.format('Modules', 'AumProcessor'))
        else:
            ValueError('Configuration file does not have {0} entry,please include it'.format('AumProcessor'))

        modules = self.config['AumProcessor']['Modules']


        self.module_loader = ModuleLoader(module_directory, modules, 'AUMProcessor')

    def add_auction_process(self, auction: Auction):
        """
        adds a Auction to auction process list

        :param auction: auction to be added
        """
        key = auction.get_key()
        action = auction.get_action()
        module_name = action.name

        action_process = AuctionProcess(auction,)

    def execute_auction(self, key: int, start: datetime, end:datetime):
        """
        Executes the allocation algorithm for the auction
        :return:
        """
        # TODO: Implement
        pass

    def add_bidding_object_to_auction_process(self, key:int, bidding_object: BiddingObject):
        """
        adds a bidding Object to auction process

        :param key: key of the auction process
        :param bidding_object: bidding object to add
        :return:
        """
        pass

    def delete_bidding_object_to_auction_process(self, key:int, bidding_object: BiddingObject):
        """
        deletes a bidding Object from auction process

        :param key: key of the auction process
        :param bidding_object: bidding object to delete
        :return:
        """
        pass

    def delete_auction_process(self, key:int):
        """
        deletes an auction process from the list
        :param key key of the auction process
        :return:
        """
        pass

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
        pass

    def get_set_field(self):
        pass