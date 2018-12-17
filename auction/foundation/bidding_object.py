#bidding_object.py
from foundation.auctioning_object import AuctioningObject

class BiddingObject(AuctioningObject):
    """
    This class respresents the bidding objects being interchanged between users and the auctionner. 
    A bidding object has two parts:
    
      1. A set of elements which establish a route description
      2. A set of options which establish the duration of the bidding object. 
    """

    def __init__(self, auction, bidding_object_key, elements, options)
        super(BiddingObject).__init__(bidding_object_key)

        self.elements = {}
        self.options = {}
        for element in elements:
            self.elements[element.name] = element
        for option in options:
            self.options[option.name] = option
        self.parent_auction = auction

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



