from aiohttp.web import run_app
from aiohttp.web import get
from aiohttp import WSCloseCode
from aiohttp import web

import pathlib
import os
import signal

from auction_server.auction_processor import AuctionProcessor
from auction_server.server_message_processor import ServerMessageProcessor
from auction_server.server_main_data import ServerMainData
from auction_server.auction_server_handler import HandleLoadAuction
from auction_server.auction_server_handler import HandleLoadResourcesFromFile

from foundation.agent import Agent
from foundation.auction_manager import AuctionManager
from foundation.session_manager import SessionManager
from foundation.resource_manager import ResourceManager
from foundation.config import Config


class AuctionServer(Agent):

    async def terminate(self, request):
        """
        Terminate server execution
        :return:
        """
        print('Send signal termination')
        os.kill(os.getpid(), signal.SIGINT)
        return web.Response(text="Terminate started")

    async def on_shutdown(self, app):
        print('on_shutdown - active sockets:', app['web_sockets'])
        # Close all open sockets
        for ws in app['web_sockets']:
            print('closing websocket')

            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='Server shutdown')
            print('websocket closed')

        # Close pending tasks
        # self.remove_auction_tasks()

    def remove_auction_tasks(self):
        """
        Removes pending tasks for all auctions as part of the shutdown process
        :return:
        """
        print("Starting remove auction tasks")
        keys = self.auction_manager.get_auctioning_object_keys()
        for key in keys:
            # Cancels all pending tasks scheduled for the auction
            if key in self._pending_tasks_by_auction:
                pending_tasks = self._pending_tasks_by_auction[key]
                for when in pending_tasks:
                    pending_tasks[when].cancel()

                self._pending_tasks_by_auction.pop(key)

        print("ending remove auction tasks")

    def __init__(self):
        try:
            super(AuctionServer, self).__init__('auction_server.yaml')

            self.logger.debug('Startig init')

            self._initialize_managers()
            self._initilize_processors()

            self._load_resources()
            self._load_auctions()

            # Start list of web sockets connected
            self.app['web_sockets'] = []

            # add routers.
            self.app.add_routes([get('/websockets', self.message_processor.handle_web_socket)])

            self.app.on_shutdown.append(self.on_shutdown)
            self.logger.debug('ending init')

        except Exception as e:
            self.logger.error("Error during server initialization - message:", str(e))

    def _load_main_data(self):
        """
        Sets the main data defined in the configuration file
        """
        self.server_data = ServerMainData()

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
        self.logger.debug("Starting _load_resources")
        auction_file = Config().get_config_param('Main', 'AuctionFile')
        base_dir = pathlib.Path(__file__).parent.parent
        auction_file = base_dir / 'xmls' / auction_file
        auction_file = str(auction_file)
        handle = HandleLoadAuction(auction_file, 0)
        handle.start()
        self.logger.debug("Ending _load_resources")

    def run(self):
        """
        Runs the application.
        :return:
        """
        if self.server_data.use_ipv6:
            run_app(self.app, host=str(self.server_data.ip_address6), port=self.server_data.local_port)
        else:
            run_app(self.app, host=str(self.server_data.ip_address4), port=self.server_data.local_port)
