# bidding_object_manager.py
from foundation.auctioning_object_manager import AuctioningObjectManager
from foundation.singleton import Singleton
from python_wrapper.ipap_message import IpapMessage

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

    def parse_message(self, ipap_message: IpapMessage)-> list:
        """

        :param ipap_message:
        :return:
        """
        #TODO: implement method.
        return []