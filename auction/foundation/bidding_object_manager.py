# bidding_object_manager.py
from .auctioning_object_manager import AuctioningObjectManager
from foundation.singleton import Singleton

class BiddingObjectManager(AuctioningObjectManager, metaclass=Singleton):

    def __init__(self, domain: int):

        super(BiddingObjectManager, self).__init__(domain)
        local_attribute = 10
        print("estoy en init")
        pass

    def set_local_attribute(self, local_attribute):
        self.local_attribute = local_attribute

    def print_local_attribute(self):
        print (self.local_attribute)