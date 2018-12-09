from foundation.auctioning_object_manager import AuctioningObjectManager
from foundation.auction import Auction
from foundation.field_def_manager import FieldDefManager
from foundation.auction_file_parser import AuctionXmlFileParser
from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainer
from datetime import datetime

class AuctionManager(AuctioningObjectManager):
    """
    This class maintains the auction within the server and client.
    """

    def __init__(self, domain:int):
        """
        Create an auction manager
        :param domain: id of the agent
        :param immediate_start: True if it should start auction right now, false otherwise.
        """
        super(AuctionManager, self).__init__(domain)
        self.time_idx = {}

    def add_auction(self, auction: Auction):
        """
        Adds an auction to the container

        :param auction: auction to add
        """
        super(AuctionManager, self).add_auctioning_object(auction)

    def delete_auction(self, auction_key : str):
        """
        Deletes an auction from the container

        :param auction_key: auction key to delete
        :return:
        """
        super(AuctionManager, self).del_actioning_object(auction_key)

    def get_auction(self, auction_key:str) -> Auction:
        """
        gets a auction from the container

        :param auction_key: key of the auction to get
        :return: Auction or an exception when not found.
        """
        return super(AuctionManager, self).get_auctioning_object(auction_key)

    def parse_auction_from_file(self, file_name: str):
        """
        parses a file in format XML and gets the registered definition of auctions
        :param file_name: file name of the file to be parsed
        """
        field_def_manager = FieldDefManager()
        auction_file_parser = AuctionXmlFileParser(super.get_domain())
        auctions = auction_file_parser.parse(file_name)
        return auctions

    def parse_ipap_message(self, ipap_message: IpapMessage, template_container : IpapTemplateContainer):
        """
        parse auctions from an ipap_message

        :param ipap_message: Message to parse
        :param template_container: container with all the registered templates
        """
        pass

    def get_ipap_message(self, auctions : list, temaplate_container: IpapTemplateContainer, use_ipv6 : bool,
                         saddress_ipv4 : str, saddress_ipv6 :str , port: int) -> IpapMessage:
        """
        get the ipap_message that contains all the auctions within the list given

        :param auctions:
        :param temaplate_container:
        :param use_ipv6:
        :param saddress_ipv4:
        :param saddress_ipv6:
        :param port:
        :return:
        """
        pass


    def increment_references(self, auctions: list, session_id : str):
        """
        This methods adds for auctions in the list a reference to the session given as parameter

        :param auctions: list of auctions to create a new reference
        :param session_id: session id to be included
        """
        pass

    def decrement_references(self, auctions: list, session_id : str):
        """
        This methods removes for auctions in the list the reference to the session given as parameter
        :param auctions: list of auctions to remove a reference
        :param session_id: session id to be excluded
        """
        pass

