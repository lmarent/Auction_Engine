
from foundation.auction import Auction
from foundation.bidding_object import BiddingObject
from foundation.auction_process_object import AuctionProcessObject
from foundation.ipap_message_parser import IpapMessageParser

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

    def __init__(self):
        self.auctions = {}

    def add_auction_process(self, auction: Auction):
        #TODO: Implement
        pass

    def execute_auction(self):
        # TODO: Implement
        pass

