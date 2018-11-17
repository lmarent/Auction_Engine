from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType

from foundation.auction import Auction
from datetime import datetime


class Resource(AuctioningObject):
    """
    This class reresents a resource that is ging to be auctioned. Examples of resources are two channels
    with different bandwidth and packet lost.

    Attributes
    ----------

    auction: sets of auction associated with the resource. They are in a dictionary to ease their access.
    start: Starting datetime when the resource must be activated.
    stop: Ending datatime whe the resource must be inactivated.
    """

    def __init__(self, key : str):
        super(Resource).__init__(key, AuctioningObjectType.RESOURCE)
        self.auctions = {}
        self.start = None
        self.stop = None

    def add_auction(self, auction : Auction):
        """
        Adds an auction to the resource
        :param auction: auction to add
        :return:
        """
        key = auction.get_key()
        if key in self.auctions.keys():
            raise ValueError("auction with key:{} is already in the resource".format(key))
        else:
            self.auctions[key] = auction

    def delete_auction(self, auction_key : str):
        """
        Deletes the auction from the resource

        :param auction_key: auction key to delete
        :return:
        """
        if auction_key in self.auctions.keys():
            del self.auctions[auction_key]
        else:
            raise ValueError("auction with key:{} is not  in the resource".format(auction_key))

    def verify_auction(self, auction : Auction):
        """
        Verifies whether or not the auction can be added to the resource

        :param auction: auction to be verified
        :return: True if it is possible to add, false otherwise.
        """
        start_auction = auction.get_start()
        stop_auction = auction.get_stop()

        for key in self.auctions:
            start = self.auctions[key].get_start()
            stop = self.auctions[key].get_stop()

            if (start_auction <= start) and (start <= stop_auction) and (stop_auction <= stop):
                return False

            if (start <= start_auction) and (stop_auction <= stop):
                return False

            if (start_auction <= stop) and (stop <= stop_auction):
                return False

        return True

    def set_start_time(self, start_time : datetime ):
        """
        Sets start time when the resource should be activated.

        :param start_time: datetime for activation
        :return:
        """
        self.start = start_time

    def set_stop_time(self, stop_time : datetime):
        """
        Sets the stop time when the resource should be inactivated

        :param stop_time: datetime for inactivation
        :return:
        """
        self.stop =stop_time