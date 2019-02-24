#bidding_object.py
from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType
from foundation.auction import Auction

class BiddingObject(AuctioningObject):
    """
    This class respresents the bidding objects being interchanged between users and the auctionner. 
    A bidding object has two parts:
    
      1. A set of elements which establish a route description
      2. A set of options which establish the duration of the bidding object. 
    """

    def __init__(self, auction_key: str, bidding_object_key:str, object_type: AuctioningObjectType,
                    elements:dict, options: dict):

        assert( object_type==AuctioningObjectType.BID or object_type==AuctioningObjectType.ALLOCATION )
        super(BiddingObject, self).__init__(bidding_object_key, object_type)

        self.elements = elements
        self.options = options
        self.parent_auction = auction_key

    def get_element_value(self, element_name):
        if element_name in self.elements.keys():
            return self.elements[element_name]
        else:
            raise ValueError('Element with name: {} was not found'.format(element_name))

    def get_option_value(self, option_name):
        if option_name in self.optios.keys():
            return self.options[option_name]
        else:
            raise ValueError('Option with name: {} was not found'.format(option_name))

