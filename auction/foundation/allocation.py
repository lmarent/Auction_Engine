
from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType


class Allocation(AuctioningObject):
    """
    Class for describing an allocation performed in the system.
    An allocation should be created everytime that we have to assign a resource to a user.
    """

    def __init__(self, auction_key: str, bid_key: str, allocation_key: str, misc_dict: dict, intervals: list):
        super(Allocation, self).__init__(allocation_key, AuctioningObjectType.ALLOCATION)
        self.auction_key = auction_key
        self.bid_key = bid_key
        self.config_params = misc_dict
        self.intervals = intervals

    def get_auction_key(self) -> str:
        """
        Gets the auction key
        :return: string
        """
        return self.auction_key

    def get_bid_key(self) -> str:
        """
        Gets the bid key
        :return: string
        """
        return self.bid_key


