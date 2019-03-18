# bidding_object_manager.py
from foundation.auctioning_object_manager import AuctioningObjectManager
from foundation.singleton import Singleton
from foundation.bidding_object import BiddingObject
from foundation.ipap_bidding_object_parser import IpapBiddingObjectParser

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainer

from typing import List
from datetime import datetime

class BiddingObjectManager(AuctioningObjectManager, metaclass=Singleton):

    def __init__(self, domain: int):

        super(BiddingObjectManager, self).__init__(domain)
        pass

    def add_bidding_object(self, bidding_object: BiddingObject):
        """
        Adds a bidding object to the container

        :param bidding_object: bidding object to add
        """
        super(BiddingObjectManager, self).add_auctioning_object(bidding_object)

    def delete_bidding_object(self, bidding_object_key: str):
        """
        Deletes a bidding object from the container

        :param bidding_object_key: bidding object key to delete
        :return:
        """
        super(BiddingObjectManager, self).del_actioning_object(bidding_object_key)

    def get_bidding_object(self, bidding_object_key: str) -> BiddingObject:
        """
        gets a bidding object from the container

        :param bidding_object_key: key of the bidding object to get
        :return: Bidding object or an exception when not found.
        """
        return super(BiddingObjectManager, self).get_auctioning_object(bidding_object_key)

    def get_done_bidding_object(self, bidding_object_key: str) -> BiddingObject:
        """
        gets a done bidding object from the container

        :param bidding_object_key: key of the bidding object to get
        :return: Bidding object or an exception when not found.
        """
        return super(BiddingObjectManager, self).get_auctioning_object_done(bidding_object_key)

    def get_bidding_object_keys(self):
        """
        Gets bidding objects keys of object registered.

        :return:
        """
        return super(BiddingObjectManager, self).get_auctioning_object_keys()

    def parse_ipap_message(self, ipap_message: IpapMessage, template_container: IpapTemplateContainer)-> List[BiddingObject]:
        """
        parse bidding objects from an ipap_message

        :param ipap_message: Message to parse
        :param template_container: container with all the registered templates
        """
        ipap_message_parser = IpapBiddingObjectParser(self.domain)
        return ipap_message_parser.parse(ipap_message, template_container)

    def get_ipap_message(self, bidding_objects: list, template_container: IpapTemplateContainer) -> IpapMessage:
        """
        get the ipap_message that contains all the bidding objects within the list given

        :param bidding_objects: bidding objects to include in the message.
        :param template_container: container with all the registered templates
        :return: ipap_message with the information
        """
        ipap_message_parser = IpapBiddingObjectParser(self.domain)
        return ipap_message_parser.get_ipap_message(bidding_objects, template_container)
