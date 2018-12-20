from aiohttp.web import Application, run_app
import asyncio

from foundation.config import Config
from foundation.parse_format import ParseFormats
from foundation.auction_manager import AuctionManager
from foundation.bidding_object_manager import BiddingObjectManager
from foundation.resource_request_manager import ResourceRequestManager

from auction_client.agent_processor import AgentProcessor

class AuctionClient:

    def __init__(self):
        try:
            self.config = Config('auction_agent.yaml').get_config()

            self.domain = ParseFormats.parse_int(self.config['Main']['Domain'])
            self.immediate_start = ParseFormats.parse_bool(self.config['Main']['ImmediateStart'])
            self._pending_tasks_by_auction = {}

            self._load_ip_address()
            self._load_database_params()
            self._initialize_managers()
            self._initilize_processors()

            # Start Listening the web server application
            self.app = Application()
            self.loop = asyncio.get_event_loop()
            self._load_resources_request()

        except Exception as e:
            print ("Error during server initialization - message:", str(e) )

    def _load_ip_address(self):
        """
        Sets the ip addreess defined in the configuration file
        """
        use_ipv6 = self.config['Control']['UseIPv6']
        use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if use_ipv6:
            self.ip_address = ParseFormats.parse_ipaddress(self.config['Control']['LocalAddr-V6'])
        else:
            self.ip_address = ParseFormats.parse_ipaddress(self.config['Control']['LocalAddr-V4'])

    def _load_database_params(self):
        """
        Loads the database parameters from configuration file
        """
        self.db_name = self.config['Postgres']['Database']
        self.db_user = self.config['Postgres']['User']
        self.db_passwd = self.config['Postgres']['Password']
        self.db_ip_address = self.config['Postgres']['Host']
        self.db_port = self.config['Postgres']['Port']

    def _initialize_managers(self):
        """
        Initializes managers used.
        :return:
        """
        self.auction_manager = AuctionManager(self.domain)
        self.bidding_object_manager = BiddingObjectManager()
        self.resource_request_manager = ResourceRequestManager()

    def _initilize_processors(self):
        """
        Initialize processors used
        :return:
        """
        if 'AUMProcessor' in self.config:
            if 'ModuleDir' in self.config['AUMProcessor']:
                module_directory = self.config['AUMProcessor']['ModuleDir']
                self.auction_processor = AgentProcessor(self.domain, module_directory)
            else:
                ValueError(
                    'Configuration file does not have {0} entry within {1}'.format('ModuleDir', 'AumProcessor'))
        else:
            raise ValueError('There should be a AUMProcessor option set in config file')

    def _load_resources_request(self):


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        # Read the configuration file
        app['config'] = config

        # Read request file.


        # schedule resource request event for auctioning with those resources.
        loop.call_soon(functools.partial(event_handler, loop))

        print('starting event loop')
        loop.call_soon(functools.partial(event_handler, loop))
        current_time = loop.time()
        new_time = current_time + 60
        print('wait', current_time, new_time)
        loop.call_at(new_time, event_handler, loop, True)
        loop.run_forever()
    finally:
        print('closing event loop')
        loop.close()