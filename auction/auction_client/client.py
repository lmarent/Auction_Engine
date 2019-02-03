from aiohttp.web import Application, run_app
from aiohttp.web import get
from aiohttp import WSCloseCode

import os, signal
import pathlib
import random

from foundation.agent import Agent
from foundation.config import Config
from foundation.auction_manager import AuctionManager
from foundation.bidding_object_manager import BiddingObjectManager

from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.agent_processor import AgentProcessor
from auction_client.client_main_data import ClientMainData
from auction_client.client_message_processor import ClientMessageProcessor
from auction_client.auction_client_handler import HandleActivateResourceRequestInterval
from auction_client.auction_client_handler import HandleRemoveResourceRequestInterval
from auction_client.resource_request import ResourceRequest


class AuctionClient(Agent):

    async def terminate(self, request):
        print('Send signal termination')
        os.kill(os.getpid(), signal.SIGINT)
        return web.Response(text="Terminate started")

    async def on_shutdown(self, app):
        self.logger.info('shutdown started')


        self.logger.info('shutdown ended')

    # async def on_startup(self, app):
    #    """
    #    method for connecting to the web server.
    #    :param app: application where the loop is taken.
    #    :return:
    #    """
    #    app['websocket_task'] = self.app.loop.create_task(self.websocket())

    def __init__(self):
        try:
            super(AuctionClient, self).__init__('auction_agent.yaml')

            self._initialize_managers()
            self._initilize_processors()

            self._load_resources_request()

            # add routers.
            self.app.add_routes([get('/terminate', self.terminate), ])

            self.app.on_shutdown.append(self.on_shutdown)

        except Exception as e:
            self.logger.error("Error during server initialization - message: {0}".format(str(e)))

    def _load_main_data(self):
        """
        Sets the main data defined in the configuration file
        """
        self.client_data = ClientMainData()

    def _initialize_managers(self):
        """
        Initializes managers used.
        :return:
        """
        self.logger.debug("Starting _initialize_managers")
        self.auction_manager = AuctionManager(self.domain)
        self.bidding_object_manager = BiddingObjectManager(self.domain)
        self.resource_request_manager = ResourceRequestManager(self.domain)
        self.auction_session_manager = AuctionSessionManager()
        self.logger.debug("Ending _initialize_managers")

    def _initilize_processors(self):
        """
        Initialize processors used
        :return:
        """
        self.logger.debug("Starting _initilize_processors")
        module_directory = Config().get_config_param('AGNTProcessor', 'ModuleDir')
        self.agent_processor = AgentProcessor(self.domain, module_directory)
        self.message_processor = ClientMessageProcessor(self.app)
        self.logger.debug("Ending _initilize_processors")

    def _load_resources_request(self):
        """
        Loads resource request registered in file
        :return:
        """
        self.logger.debug("Starting _load_resources_request")
        resource_request_file = Config().get_config_param('Main', 'ResourceRequestFile')
        base_dir = pathlib.Path(__file__).parent.parent
        resource_request_file = base_dir / 'xmls' / resource_request_file
        resource_request_file = str(resource_request_file)
        resource_requests = self.resource_request_manager.parse_resource_request_from_file(resource_request_file)

        self.logger.debug("resource_request to read:{0}".format(len(resource_requests)))

        # schedule the new events.
        for request in resource_requests:
            ret_start, ret_stop = self.resource_request_manager.add_resource_request(request)
            for start in ret_start:
                when = self._calculate_when(start)
                handle_activate = HandleActivateResourceRequestInterval(start, ret_start[start], when)
                handle_activate.start()
                request.add_task(handle_activate)

            for stop in ret_stop:
                when = self._calculate_when(stop)
                handle_remove = HandleRemoveResourceRequestInterval(stop, ret_stop[stop], when)
                handle_remove.start()
                request.add_task(handle_remove)

        self.logger.debug("Ending _load_resources_request")

    def run(self):
        """
        Runs the application.
        :return:
        """
        self.client_data.source_port = random.randint(1024, 65000)
        if self.client_data.use_ipv6:
            print(self.client_data.ip_address6, self.client_data.source_port)
            run_app(self.app, host=str(self.client_data.ip_address6), port=self.client_data.source_port)
        else:
            print(self.client_data.ip_address4, self.client_data.source_port)
            run_app(self.app, host=str(self.client_data.ip_address4), port=self.client_data.source_port)


if __name__ == '__main__':
    agent = AuctionClient()
    agent.run()
