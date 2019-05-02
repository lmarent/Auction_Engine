from aiohttp.web import run_app
from aiohttp.web import get
from aiohttp import web

import pathlib
import os
import signal
from copy import deepcopy
import asyncio

from auction_server.auction_processor import AuctionProcessor
from auction_server.server_message_processor import ServerMessageProcessor
from auction_server.server_main_data import ServerMainData
from auction_server.auction_server_handler import HandleLoadAuction
from auction_server.auction_server_handler import HandleLoadResourcesFromFile
from auction_server.auction_server_handler import HandleClientTearDown
from auction_server.auction_session import AuctionSession
from auction_server.server_message_processor import ClientConnectionState


from foundation.agent import Agent
from foundation.auction_manager import AuctionManager
from foundation.session_manager import SessionManager
from foundation.resource_manager import ResourceManager
from foundation.config import Config

from utils.auction_utils import log

class AuctionServer(Agent):

    def __init__(self):
        try:
            super(AuctionServer, self).__init__('auction_server.yaml')

            self.logger.debug('Startig init')

            self._initialize_managers()
            self._initilize_processors()

            self._load_resources()
            self._load_auctions()

            # add routers.
            self.app.add_routes([get('/websockets', self.message_processor.handle_web_socket)])

            self.app.on_shutdown.append(self.on_shutdown)
            self.logger.debug('ending init')

        except Exception as e:
            self.logger.error("Error during server initialization - message:", str(e))


    async def terminate(self, request):
        """
        Terminate server execution
        :return:
        """
        print('Send signal termination')
        os.kill(os.getpid(), signal.SIGINT)
        return web.Response(text="Terminate started")

    async def on_shutdown(self, app):
        """
        Close all open connections
        :param app:
        :return:
        """

        session_keys = deepcopy(self.session_manager.get_session_keys())

        for session_key in session_keys:
            session: AuctionSession = self.session_manager.get_session(session_key)
            handle_client_teardown = HandleClientTearDown(session.get_connection())
            await handle_client_teardown.start()

        # Wait while there are still open connections
        while True:
            await asyncio.sleep(1)

            num_open = 0
            for session in self.auction_session_manager.session_objects.values():
                if session.connection.get_state() != ClientConnectionState.CLOSED:
                    num_open = num_open + 1

        # remove auctions and their processes
        await self.remove_auctions()

    async def remove_auctions(self):
        """
        Removes auctions and their related objects as part of the shutdown process
        :return:
        """
        self.logger.debug("Starting remove auctions")

        keys = self.auction_manager.get_auctioning_object_keys()
        for key in keys:
            auction = self.auction_manager.get_auction(key)
            self.auction_processor.delete_auction(auction)
            await auction.stop_tasks()
            self.auction_manager.delete_auction(key)

        self.logger.debug("ending remove auctions")

    def _load_main_data(self):
        """
        Sets the main data defined in the configuration file
        """
        self.logger.debug("Starting _load_main_data")
        self.server_data = ServerMainData()
        self.logger.debug("Ending _load_main_data")

    def _initialize_managers(self):
        """
        Initializes managers used.
        :return:
        """
        self.logger.debug("Starting _initialize_managers")
        self.auction_manager = AuctionManager(self.domain)
        #       self.bidding_object_manager = BiddingObjectManager()
        self.session_manager = SessionManager()
        self.resource_manager = ResourceManager(self.domain)
        self.logger.debug("Ending _initialize_managers")

    def _initilize_processors(self):
        """
        Initialize processors used
        :return:
        """
        self.logger.debug("Starting _initilize_processors")
        module_directory = Config().get_config_param('AUMProcessor', 'ModuleDir')
        self.auction_processor = AuctionProcessor(self.domain, module_directory)
        self.message_processor = ServerMessageProcessor()
        self.logger.debug("Ending _initilize_processors")

    def _load_resources(self):
        """
        Loads resources from file
        :return:
        """
        self.logger.debug("Starting _load_resources")

        try:
            resource_file = Config().get_config_param('Main', 'ResourceFile')
            base_dir = pathlib.Path(__file__).parent.parent
            resource_file = base_dir / 'config' / resource_file
            handle = HandleLoadResourcesFromFile(resource_file, 0)
            handle.start()
        except Exception as e:
            self.logger.error("An error occours during load resource", str(e))
        self.logger.debug("Ending _load_resources")

    def _load_auctions(self):
        """
        Loads auctions from file
        :return:
        """
        self.logger.debug("Starting _load_auctions")
        auction_file = Config().get_config_param('Main', 'AuctionFile')
        base_dir = pathlib.Path(__file__).parent.parent
        auction_file = base_dir / 'xmls' / auction_file
        auction_file = str(auction_file)
        handle = HandleLoadAuction(auction_file, 0)
        handle.start()
        self.logger.debug("Ending _load_auctions")

    def run(self):
        """
        Runs the application.
        :return:
        """
        if self.server_data.use_ipv6:
            run_app(self.app, host=str(self.server_data.ip_address6), port=self.server_data.local_port)
        else:
            run_app(self.app, host=str(self.server_data.ip_address4), port=self.server_data.local_port)
