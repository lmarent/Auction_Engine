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

from python_wrapper.ipap_template_container import IpapTemplateContainer


class AuctionServer:

    def __init__(self):

        self.app = Application()

        self.conf = Config('auction_server.yaml').get_config()

        self.domain = ParseFormats.parse_int(self.conf['Main']['Domain'])
        self.auctioner_templates = {}
        self.auctioner_templates[self.domain] = IpapTemplateContainer()
        self._load_ip_address()
        self._load_database_params()
        self._initialize_managers()
        self._initilize_processors()
        self.loop = asyncio.get_event_loop()
        self._load_resources()

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
        self.handle_add_resource('resources.yaml')

    def _load_auctions(self):
        """
        Loads auctions from file
        :return:
        """
        # handle_add_resource(self.loop)
        pass

    def handle_add_resource(self, file_name: str):
        """
        Handle adding a new resource to the auction server
        """
        base_dir = pathlib.Path(__file__).parent.parent
        if file_name:
            resource_file = base_dir / 'config' / file_name
            with open(resource_file) as f:
                resource_sets = yaml.load(f)
                for resource_set in resource_sets:
                    for resource in resource_sets[resource_set]:
                        resource = Resource(resource_set + '.' + resource)
                        self.resource_manager.add_auctioning_object(resource)

        else:
            raise ValueError("Invalid file name")

    def run(self):
        """
        Runs the application.
        :return:
        """
        run_app(self.app)

