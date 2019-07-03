# bidding_object_manager.py
from builtins import bool

from foundation.auctioning_object_manager import AuctioningObjectManager
from foundation.singleton import Singleton
from foundation.bidding_object import BiddingObject
from foundation.ipap_bidding_object_parser import IpapBiddingObjectParser
from foundation.auction_manager import AuctionManager
from foundation.bidding_object_file_parser import BiddingObjectXmlFileParser
from foundation.config import Config
from foundation.database_manager import DataBaseManager

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainer

from typing import List
from typing import DefaultDict
from collections import defaultdict
from utils.auction_utils import log


class BiddingObjectManager(AuctioningObjectManager, metaclass=Singleton):

    def __init__(self, domain: int):

        super(BiddingObjectManager, self).__init__(domain)
        self.index_by_session : DefaultDict[str, list] = defaultdict(list)
        self.index_by_parent :DefaultDict[str, list] = defaultdict(list)
        self.logger = log().get_logger()
        try:
            self.store_objects = Config().get_config_param('Main', 'StoreObjects')
        except ValueError:
            self.store_objects = False # by default does not store objects.

        pass

    async def add_bidding_object(self, bidding_object: BiddingObject):
        """
        Adds a bidding object to the container

        :param bidding_object: bidding object to add
        """
        assert bidding_object.get_session(), "Error, you are triying to store a bidding \
                                                    object which is not attached to a session"

        super(BiddingObjectManager, self).add_auctioning_object(bidding_object)
        self.logger.info("adding bidding objectkey {0} - session {1}".format(bidding_object.get_key(),
                                                                             bidding_object.get_session()))

        if bidding_object.get_session() not in self.index_by_session:
            self.index_by_session[bidding_object.get_session()] = []
        (self.index_by_session[bidding_object.get_session()]).append(bidding_object.get_key())

        if bidding_object.get_parent_key() not in self.index_by_parent:
            self.index_by_parent[bidding_object.get_parent_key()] = []
        (self.index_by_parent[bidding_object.get_parent_key()]).append(bidding_object.get_key())

        # stores the bidding object in the database.

        if self.store_objects:
            self.logger.info("It is going to insert bidding object: {0}".format(bidding_object.get_key()))
            database_manager = DataBaseManager()
            self.logger.info("database object created bididng object: {0}".format(id(database_manager)))
            connection = await database_manager.acquire()
            self.logger.info("connection acquired")
            await bidding_object.store(connection)
            await database_manager.release(connection)
            self.logger.info("It stored objects the object: {0}".format(bidding_object.get_key()))

    def delete_bidding_object(self, bidding_object_key: str):
        """
        Deletes a bidding object from the container, it also removes it from the session index.

        :param bidding_object_key: bidding object key to delete
        :return:
        """
        self.logger.info("delete bidding object key {0}".format(bidding_object_key))

        bidding_object = self.get_bidding_object(bidding_object_key)
        super(BiddingObjectManager, self).del_actioning_object(bidding_object_key)
        self.index_by_session[bidding_object.get_session()].remove(bidding_object_key)
        self.index_by_parent[bidding_object.get_parent_key()].remove(bidding_object_key)

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

    def parse_bidding_objects(self, filename: str) -> List[BiddingObject]:
        """
        Parses bidding objects within the xml file

        :param filename: file name to parse.
        :return:
        """
        file_parser = BiddingObjectXmlFileParser(self.domain)
        return  file_parser.parse(filename)

    def parse_ipap_message(self, ipap_message: IpapMessage, template_container: IpapTemplateContainer)-> List[BiddingObject]:
        """
        parse bidding objects from an ipap_message

        :param ipap_message: Message to parse
        :param template_container: container with all the registered templates
        """
        ipap_message_parser = IpapBiddingObjectParser(self.domain)
        return ipap_message_parser.parse(ipap_message, template_container)

    def get_ipap_message(self, bidding_objects: List[BiddingObject], template_container: IpapTemplateContainer) -> IpapMessage:
        """
        get the ipap_message that contains all the bidding objects within the list given

        :param bidding_objects: bidding objects to include in the message.
        :param template_container: container with all the registered templates
        :return: ipap_message with the information
        """
        ipap_bidding_object_parser = IpapBiddingObjectParser(self.domain)
        message = IpapMessage(self.domain, IpapMessage.IPAP_VERSION, True)
        auction_manager = AuctionManager(self.domain)

        for bidding_object in bidding_objects:
            auction = auction_manager.get_auction(bidding_object.get_parent_key())
            ipap_bidding_object_parser.get_ipap_message(bidding_object, auction, template_container, message)

        return message

    def get_bidding_objects_by_session(self, session_key: str):
        """
        gets the bidding objects attached to a particular session

        :param session_key: session key to return the bidding objects
        :return: list of bidding object keys
        """
        if session_key in self.index_by_session:
            return self.index_by_session[session_key]
        else:
            raise ValueError('Session key {0} does not exist in the bidding object container'.format(session_key))

    def get_bidding_objects_by_parent(self, parent_key: str):
        """
        Gets the bidding objects attached to a particular parent

        :param parent_key: parent key to return the bidding objects
        :return: list of bidding object keys
        """
        if parent_key in self.index_by_parent:
            return self.index_by_parent[parent_key]
        else:
            raise ValueError('Parent key {0} does not exist in the bidding object container'.format(parent_key))
