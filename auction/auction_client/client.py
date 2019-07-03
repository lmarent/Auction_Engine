from aiohttp.web import run_app
from aiohttp.web import get
from aiohttp import web

import os, signal
import pathlib
import random
import asyncio

from foundation.agent import Agent
from foundation.config import Config
from foundation.auction_manager import AuctionManager
from foundation.bidding_object_manager import BiddingObjectManager
from foundation.database_manager import DataBaseManager

from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.agent_processor import AgentProcessor
from auction_client.client_main_data import ClientMainData
from auction_client.client_message_processor import ClientMessageProcessor
from auction_client.auction_client_handler import HandleActivateResourceRequestInterval
from auction_client.auction_client_handler import HandleRemoveResourceRequestInterval
from auction_client.auction_client_handler import HandleResourceRequestTeardown
from auction_client.server_connection import ServerConnectionState

from utils.auction_utils import DateUtils
from copy import deepcopy


class AuctionClient(Agent):

    async def on_shutdown(self, app):
        self.logger.info('shutdown started')

        # terminate pending interval request tasks
        session_keys = deepcopy(self.auction_session_manager.get_session_keys())
        for session_key in session_keys:
            session = self.auction_session_manager.get_session(session_key)
            handle_resource_request_teardown = HandleResourceRequestTeardown(session_key)
            await handle_resource_request_teardown.start()

            # teardowns the session created.
            await self.message_processor.process_disconnect(session)

            # remove the session from the session manager
            self.auction_session_manager.del_session(session_key)


        while True:
            await asyncio.sleep(1)

            num_open = 0
            for session in self.auction_session_manager.session_objects.values():
                if session.server_connection.get_state() != ServerConnectionState.CLOSED:
                    num_open = num_open + 1

            if num_open == 0:
                break

        try:
            await self.database_manager.close()
        except ValueError:
            pass

        self.logger.info('shutdown ended')

    def __init__(self):
        try:
            super(AuctionClient, self).__init__('auction_agent.yaml')

            self._initialize_managers()

            self.logger.debug("ads 1")
            self._initilize_processors()

            self.logger.debug("ads 2")
            self._load_resources_request()

            # add routers.
            self.app.add_routes([get('/terminate', self.terminate), ])

            # add handler for shutdown the process.
            self.app.on_shutdown.append(self.on_shutdown)
            self.app.on_startup.append(self.on_startup)

        except Exception as e:
            self.logger.error("Error during server initialization - message: {0}".format(str(e)))

    async def terminate(self, request):
        print('Send signal termination')
        os.kill(os.getpid(), signal.SIGINT)
        return web.Response(text="Terminate started")

    # async def on_startup(self, app):
    #    """
    #    method for connecting to the web server.
    #    :param app: application where the loop is taken.
    #    :return:
    #    """
    #    app['websocket_task'] = self.app.loop.create_task(self.websocket())

    async def on_startup(self, app):
        """
        Connects to the database,
        :param app: application connecting the database
        :return:
        """
        self.logger.debug("Starting On startup")
        await self.database_manager.connect()
        self.logger.debug("Ending On startup")


    def _load_main_data(self):
        """
        Sets the main data defined in the configuration file
        """
        self.logger.debug("starting _load_main_data")
        self.client_data = ClientMainData()
        self.logger.debug("ending _load_main_data")

    def _initialize_managers(self):
        """
        Initializes managers used.
        :return:
        """
        self.logger.debug("Starting _initialize_managers")
        self.auction_manager = AuctionManager(self.domain)
        self.database_manager = DataBaseManager(Config().get_config_param('DataBase', 'Type'),
                                                Config().get_config_param('DataBase', 'Host'),
                                                Config().get_config_param('DataBase', 'User'),
                                                Config().get_config_param('DataBase', 'Password'),
                                                Config().get_config_param('DataBase', 'Port'),
                                                Config().get_config_param('DataBase', 'DbName'),
                                                Config().get_config_param('DataBase', 'MinSize'),
                                                Config().get_config_param('DataBase', 'MaxSize'))
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

        self.logger.debug("Nbr resource requests to read:{0}".format(len(resource_requests)))

        # schedule the new events.
        for request in resource_requests:
            try:
                ret_start, ret_stop = self.resource_request_manager.add_resource_request(request)
                for start in ret_start:
                    when = DateUtils().calculate_when(start)
                    handle_activate = HandleActivateResourceRequestInterval(start, ret_start[start], when)
                    request.add_task(handle_activate)
                    handle_activate.start()

                for stop in ret_stop:
                    when = DateUtils().calculate_when(stop)
                    handle_remove = HandleRemoveResourceRequestInterval(stop, ret_stop[stop], when)
                    request.add_task(handle_remove)
                    handle_remove.start()
            except ValueError as e:
                self.logger.error(str(e))
        self.logger.debug("Ending _load_resources_request")

    def run(self):
        """
        Runs the application.
        :return:
        """
        self.client_data.source_port = random.randint(1024, 65000)
        if self.client_data.use_ipv6:
            run_app(self.app, host=str(self.client_data.ip_address6), port=self.client_data.source_port)
        else:
            run_app(self.app, host=str(self.client_data.ip_address4), port=self.client_data.source_port)
