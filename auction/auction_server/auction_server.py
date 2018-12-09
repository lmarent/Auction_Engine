from aiohttp.web import Application, run_app
import asyncio
import functools
import pathlib
import yaml
from foundation.resource import Resource


from foundation.auction_manager import AuctionManager
#from foundation.bidding_object_manager import BiddingObjectManager
from foundation.session_manager import SessionManager
from foundation.resource_manager import ResourceManager
from foundation.config import Config
from foundation.parse_format import ParseFormats
from foundation.auction_file_parser import AuctionXmlFileParser

from python_wrapper.ipap_template_container import IpapTemplateContainer


class AuctionServer:

    def __init__(self):

        self.conf = Config('auction_server.yaml').get_config()

        self.domain = ParseFormats.parse_int(self.conf['Main']['Domain'])
        self._load_ip_address()
        self._load_database_params()
        self._initialize_managers()
        self._initilize_processors()

        # Start Listening the web server application
        self.app = Application()
        self.loop = asyncio.get_event_loop()
        self._load_resources()
        self._load_auctions()

    def _load_ip_address(self):
        """
        Sets the ip addreess defined in the configuration file
        """
        use_ipv6 = self.conf['Control']['UseIPv6']
        use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if use_ipv6:
            self.ip_address = ParseFormats.parse_ipaddress(self.conf['Control']['LocalAddr-V6'])
        else:
            self.ip_address = ParseFormats.parse_ipaddress(self.conf['Control']['LocalAddr-V4'])

    def _load_database_params(self):
        """
        Loads the database parameters from configuration file
        """
        self.db_name = self.conf['Postgres']['Database']
        self.db_user = self.conf['Postgres']['User']
        self.db_passwd = self.conf['Postgres']['Password']
        self.db_ip_address = self.conf['Postgres']['Host']
        self.db_port = self.conf['Postgres']['Port']

    def _initialize_managers(self):
        """
        Initializes managers used.
        :return:
        """
        self.auction_manager = AuctionManager(self.domain)
#       self.bidding_object_manager = BiddingObjectManager()
        self.session_manager = SessionManager()
        self.resource_manager = ResourceManager(self.domain)

    def _initilize_processors(self):
        """
        Initialize processors used
        :return:
        """
        pass


    def _load_resources(self):
        """
        Loads resources from file
        :return:
        """
        if 'ResourceFile' in self.conf:
            base_dir = pathlib.Path(__file__).parent.parent
            resource_file = self.conf['ResourceFile']
            resource_file = base_dir / 'config' / resource_file
            self.handle_load_resources(resource_file)
        else:
            raise ValueError("The Resource File ({}) configuration option does not exist!".format('ResourceFile'))

    def _load_auctions(self):
        """
        Loads auctions from file
        :return:
        """
        if 'AuctionFile' in self.conf:
            auction_file = self.conf['AuctionFile']
            base_dir = pathlib.Path(__file__).parent.parent
            auction_file = base_dir / 'xmls' / auction_file
            auction_file = str(auction_file)
            self.handle_load_auctions(auction_file)
        else:
            raise ValueError("The Auction File ({}) configuration option does not exist!".format('AuctionFile'))

    def handle_load_resources(self, file_name: str):
        """
        Handles adding the resources defined in the file given to the auction server.
        The file name includes the absolute path.
        """
        try:
            with open(file_name) as f:
                resource_sets = yaml.load(f)
                for resource_set in resource_sets:
                    for resource in resource_sets[resource_set]:
                        resource = Resource(resource_set + '.' + resource)
                        self.resource_manager.add_auctioning_object(resource)
        except IOError as e:
            raise ValueError("Error opening file - Message:", str(e))

    def handle_load_auctions(self, file_name: str):
        """
        Handles auction loading from file.

        :param file_name: name of he auction xml file to load
        :return:
        """
        auction_file_parser = AuctionXmlFileParser(self.domain)
        auctions = auction_file_parser.parse(file_name)
        for auction in auctions:
            if self.resource_manager.verify_auction(auction):
                self.auction_manager.add_auction(auction)
            else:
                print("The auction with key {0} could not be added".format(auction.get_key()))

    def run(self):
        """
        Runs the application.
        :return:
        """
        run_app(self.app)
