from aiohttp.web import run_app
from aiohttp.web import WebSocketResponse
from aiohttp.web import get
from aiohttp import WSMsgType
from aiohttp import WSCloseCode
from aiohttp import web

import functools
import pathlib
import yaml
import os,signal
from datetime import datetime, timedelta

from auction_server.auction_processor import AuctionProcessor

from foundation.agent import Agent
from foundation.resource import Resource
from foundation.auction_manager import AuctionManager
from foundation.session_manager import SessionManager
from foundation.resource_manager import ResourceManager
from foundation.auction_file_parser import AuctionXmlFileParser
from foundation.auction import Auction
from foundation.auctioning_object import AuctioningObjectState
from foundation.interval import Interval
from foundation.config import Config
from foundation.parse_format import ParseFormats


class AuctionServer(Agent):

    async def terminate(self, request):
        """
        Terminate server execution
        :return:
        """
        print('Send signal termination')
        os.kill(os.getpid(), signal.SIGINT)
        return web.Response(text="Terminate started")

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

    async def callback_message(self, msg):
        print(msg)

    async def handle_web_socket(self, request):
        ws = WebSocketResponse()
        await ws.prepare(request)

        # Put in the list the new connection from the client.
        request.app['web_sockets'].append(ws)
        try:
            async for msg in ws:
                if msg.type == WSMsgType.text:
                    await self.callback_message(msg)

                elif msg.type == WSMsgType.error:
                    self.logger.debug('ws connection closed with exception %s' % ws.exception())

                elif msg.type == WSMsgType.close:
                    self.logger.debug('ws connection closed')
        finally:
            request.app['web_sockets'].remove(ws)

        self.logger.debug('websocket connection closed')
        return ws

    def __init__(self):
        try:
            super(AuctionServer, self).__init__('auction_server.yaml')

            self.logger.debug('Startig init')

            # self._initialize_managers()
            # self._initilize_processors()

            #self._load_resources()
            # self._load_auctions()

            # add routers.
            self.app.add_routes([get('/websockets', self.handle_web_socket)])

            # Start list of web sockets connected
            self.app['web_sockets'] = []


            self.app.on_shutdown.append(self.on_shutdown)
            self.logger.debug('ending init')

        except Exception as e:
            self.logger.error("Error during server initialization - message:", str(e))

    def _load_main_data(self):
        """
        Sets the main data defined in the configuration file
        """
        self.logger.debug("Stating _load_main_data")


        use_ipv6 = Config().get_config_param('Main','UseIPv6')
        self.use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if self.use_ipv6:
            self.ip_address6 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V6'))
        else:
            self.ip_address4 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V4'))

        # Gets default ports (origin, destination)
        self.local_port = ParseFormats.parse_uint16(Config().get_config_param('Main','LocalPort'))
        self.protocol = ParseFormats.parse_uint8( Config().get_config_param('Main','DefaultProtocol'))
        self.life_time = ParseFormats.parse_uint8( Config().get_config_param('Main','LifeTime'))

        self.logger.debug("ending _load_main_data")


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
            self.handle_load_resources(resource_file)
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
        self.handle_load_auctions(auction_file)
        self.logger.debug("Ending _load_resources")

    def handle_load_resources(self, file_name: str):
        """
        Handles adding the resources defined in the file given to the auction server.
        The file name includes the absolute path.
        """
        self.logger.debug("Starting handle_load_resources")
        try:
            with open(file_name) as f:
                resource_sets = yaml.load(f)
                for resource_set in resource_sets:
                    for resource in resource_sets[resource_set]:
                        resource = Resource(resource_set.lower() + '.' + resource.lower())
                        self.resource_manager.add_auctioning_object(resource)
            self.logger.debug("Ending handle_load_resources")
        except IOError as e:
            self.logger.error("Error opening file - Message: {0}".format(str(e)))
            raise ValueError("Error opening file - Message:", str(e))

    def handle_load_auctions(self, file_name: str):
        """
        Handles auction loading from file.

        :param file_name: name of he auction xml file to load
        :return:
        """
        self.logger.debug("Starting handle_load_auctions")
        try:
            auction_file_parser = AuctionXmlFileParser(self.domain)
            auctions = auction_file_parser.parse(file_name)
            for auction in auctions:
                if self.resource_manager.verify_auction(auction):
                    self.auction_manager.add_auction(auction)

                    # Schedule auction activation
                    if self.immediate_start:
                        when = self.app.loop.time()
                        self.app.loop.call_soon(functools.partial(self.handle_activate_auction, auction, when))
                    else:
                        when = self._calculate_when(auction.get_start())
                        call = self.app.loop.call_at(when, self.handle_activate_auction, auction, when)
                        self._add_pending_tasks(auction.get_key(), call, when)

                    # Schedule auction removal
                    when = self._calculate_when(auction.get_stop())
                    call = self.app.loop.call_at(when, self.handle_remove_auction, auction, when)
                    self._add_pending_tasks(auction.get_key(), call, when)
                else:
                    print("The auction with key {0} could not be added".format(auction.get_key()))
        except Exception as e:
            self.logger.error("An error occur during load actions - Error:{}".format(str(e)))

        self.logger.debug("Ending handle_load_auctions")

    def handle_activate_auction(self, auction: Auction, when: float):
        """
        Activates an auction

        :param auction: auction to activate
        :param when: seconds when the auction should be activate
        """
        self.logger.debug('Starting handle activate auction')
        try:
            # The task is no longer scheduled.
            self._remove_pending_task(auction.get_key(), when)

            # creates the auction processor
            self.auction_processor.add_auction_process(auction)
            start = auction.get_start()
            stop = auction.get_stop()
            interval = auction.get_interval()

            # Activates its execution
            when = self._calculate_when(auction.get_start())
            call = self.app.loop.call_at(when, self.handle_push_execution, auction, start, stop, interval, when)
            self._add_pending_tasks(auction.get_key(), call, when)

            # Change the state of all auctions to active
            auction.set_state(AuctioningObjectState.ACTIVE)
        except Exception as e:
            self.logger.error("Auction {0} could not be activated - error: {1}".format(auction.get_key(), str(e)))
        self.logger.debug('Ending handle activate auction')

    def handle_remove_auction(self, auction: Auction, when: float):
        """
        Removes an auction

        :param auction: auction to remove
        :param when: seconds when the auction should be activate
        """
        self.logger.debug('Starting handle remove auction')

        # The task is no longer scheduled.
        self._remove_pending_task(auction.get_key(), when)

        # Cancels all pending task scheduled for the auction
        for when in self._pending_tasks_by_auction[auction.get_key()]:
            call = self._pending_tasks_by_auction[auction.get_key()][when]
            call.cancel()

        self._pending_tasks_by_auction.pop(auction.get_key())

        self.logger.debug('Ending handle remove auction')

    def handle_push_execution(self, auction: Auction, start: datetime, stop: datetime, interval: Interval, when: float):
        """

        :param auction:
        :param start:
        :param stop:
        :param interval:
        :param when:
        :return:
        """
        self.logger.debug('starting handle push execution')

        # The task is no longer scheduled.
        self._remove_pending_task(auction.get_key(), when)

        stop_tmp = start + timedelta(seconds=interval.interval)

        if stop_tmp > stop:
            stop_tmp = stop

        # execute the algorithm
        self.auction_processor.execute_auction(auction.get_key(), start, stop_tmp)

        if stop_tmp < stop:
            when = self._calculate_when(stop_tmp)
            call = self.app.loop.call_at(when, self.handle_push_execution, auction, stop_tmp, stop, interval, when)
            self._add_pending_tasks(auction.get_key(), call, when)

        print('interval:', interval.align)

        self.logger.debug('ending handle push execution')

    def run(self):
        """
        Runs the application.
        :return:
        """
        if self.use_ipv6:
            run_app(self.app, host=str(self.ip_address6), port=self.local_port)
        else:
            run_app(self.app, host=str(self.ip_address4), port=self.local_port)

