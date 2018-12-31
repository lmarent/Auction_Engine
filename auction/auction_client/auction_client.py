from aiohttp.web import Application, run_app
import asyncio
from datetime import datetime

from foundation.agent import Agent
from foundation.config import Config
from foundation.parse_format import ParseFormats
from foundation.auction_manager import AuctionManager
from foundation.bidding_object_manager import BiddingObjectManager

from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.agent_processor import AgentProcessor
from auction_client.resource_request import ResourceRequest

class AuctionClient(Agent):

    def __init__(self):
        try:
            self.config = Config('auction_agent.yaml').get_config()

            self.domain = ParseFormats.parse_int(self.config['Main']['Domain'])
            self.immediate_start = ParseFormats.parse_bool(self.config['Main']['ImmediateStart'])

            self._load_ip_address()
            self._load_control_port()
            self._load_database_params()
            self._initialize_managers()
            self._initilize_processors()

            super(AuctionClient, self).__init__()

            self._load_resources_request()

        except Exception as e:
            print ("Error during server initialization - message:", str(e) )

    def _load_ip_address(self):
        """
        Sets the ip addreess defined in the configuration file
        """
        use_ipv6 = self.config['Control']['UseIPv6']
        self.use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if self.use_ipv6:
            self.ip_address6 = ParseFormats.parse_ipaddress(self.config['Control']['LocalAddr-V6'])
        else:
            self.ip_address4 = ParseFormats.parse_ipaddress(self.config['Control']['LocalAddr-V4'])

    def _load_control_port(self):
        """
        Sets the control por defined in the configuration file
        """
        try:

            self.port = ParseFormats.parse_uint16(self.config['Control']['ControlPort'])

        except ValueError as verr:
            raise ValueError("The value for control port{0} is not a valid number".format(
                            self.config['Control']['ControlPort']))


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
        self.auction_session_manager = AuctionSessionManager()

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
        if 'Main' in self.config:
            raise ValueError("The main section was not defined in configuration option file")

        if 'ResourceRequestFile' in self.config['Main']:
            raise ValueError("The ResourceRequestFile option is not defined in the main section \
                                of the configuration file")

        resource_request_file = self.config['Main']['ResourceRequestFile']
        resource_requests = self.resource_request_manager.parse_resource_request_from_file(resource_request_file)

        # schedule the new events.
        for request in resource_requests:
            ret_start, ret_stop = self.resource_request_manager.add_resource_request(request)
            for start in ret_start:
                when = self._calculate_when(start)
                call = self.loop.call_at(when, self.handle_activate_resource_request, start, ret_start[start], when)
                self._add_pending_tasks(ret_start[start].get_key(), call, when)

            for stop in ret_stop:
                when = self._calculate_when(stop)
                call = self.loop.call_at(when, self.handle_remove_resource_request, stop, ret_stop[stop], when)
                self._add_pending_tasks(ret_stop[stop].get_key(), call, when)
    :
    def handle_activate_resource_request(self, start:datetime,
                                         resource_request: ResourceRequest, when: float):
        print('start handle activate resource request')

        # The task is no longer scheduled.
        self._remove_pending_task(resource_request.get_key(), when)

        # for now we request to any resource,
        # a protocol to spread resources available must be implemented
        resource_id = "ANY"
        interval = resource_request.get_interval_by_start_time(start)

        # Gets an ask message for the resource
        message = self.resource_request_manager.get_ipap_message(resource_request, start,
                                                       resource_id, self.use_ipv6,
                                                       self.ip_address4, self.ip_address6,
                                                       self.port)

        # Create a new session for sending the request
        self.auction_session_manager.create_agent_session()

        print('ending handle activate resource request')

    def handle_remove_resource_request(self):

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