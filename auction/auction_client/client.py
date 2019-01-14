from aiohttp.web import Application, run_app
from aiohttp import web, WSMsgType
from datetime import datetime
from aiohttp.web import get
from aiohttp import ClientSession
from aiohttp import WSCloseCode

import os,signal
import pathlib
import random

from foundation.agent import Agent
from foundation.config import Config
from foundation.parse_format import ParseFormats
from foundation.auction_manager import AuctionManager
from foundation.bidding_object_manager import BiddingObjectManager

from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.resource_request import ResourceRequest
from auction_client.agent_processor import AgentProcessor

class AuctionClient(Agent):

    async def terminate(self, request):
        print('Send signal termination')
        os.kill(os.getpid(), signal.SIGINT)
        return web.Response(text="Terminate started")

    async def on_shutdown(self, app):

        # Close open sockets
        await self.app['ws'].close(code=WSCloseCode.GOING_AWAY,
                            message='Client shutdown')
        await self.app['session'].close()

    async def callback(self, msg):
        print(msg)

    async def websocket(self, session):

        if self.use_ipv6:
            destin_ip_address = str(self.destination_address6)
        else:
            destin_ip_address = str(self.destination_address4)

        # TODO: CONNECT USING A DNS
        print('connect to ', destin_ip_address, self.destination_port)
        http_address = 'http://{ip}:{port}/{resource}'.format(ip=destin_ip_address,
                                                    port=str(self.destination_port),
                                                    resource='websockets')
        async with session.ws_connect(http_address) as ws:
            self.app['ws'] = ws
            self.app['session'] = session
            async for msg in ws:
                print(msg.type)
                if msg.type == WSMsgType.TEXT:
                    await self.callback(msg.data)
                elif msg.type == WSMsgType.CLOSED:
                    self.logger.error("websocket closed by the server.")
                    print("websocket closed by the server.")
                    break
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error("websocket error received.")
                    print("websocket error received.")
                    break

    async def on_startup(self, app):
        session = ClientSession()
        app['websocket_task'] = self.loop.create_task(self.websocket(session))

    def __init__(self):
        try:
            super(AuctionClient, self).__init__('auction_agent.yaml')

            self._initialize_managers()
            self._initilize_processors()

            self._load_resources_request()

            # add routers.
            self.app.add_routes([get('/terminate', self.terminate),])

            self.app.on_startup.append(self.on_startup)
            self.app.on_shutdown.append(self.on_shutdown)

        except Exception as e:
            self.logger.error("Error during server initialization - message: {0}".format(str(e)) )

    def _load_main_data(self):
        """
        Sets the main data defined in the configuration file
        """
        self.logger.debug("Stating _load_main_data auction client")

        use_ipv6 = Config().get_config_param('Main','UseIPv6')
        self.use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if self.use_ipv6:
            self.ip_address6 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V6'))
            self.destination_address6 = ParseFormats.parse_ipaddress(
                            Config().get_config_param('Main','DefaultDestinationAddr-V6'))
        else:
            self.ip_address4 = ParseFormats.parse_ipaddress(Config().get_config_param('Main','LocalAddr-V4'))
            self.destination_address4 = ParseFormats.parse_ipaddress(
                            Config().get_config_param('Main','DefaultDestinationAddr-V4'))

        # Gets default ports (origin, destination)
        self.source_port = ParseFormats.parse_uint16(Config().get_config_param('Main','DefaultSourcePort'))
        print('self.source_port', self.source_port, Config().get_config_param('Main','DefaultSourcePort'))
        self.destination_port = ParseFormats.parse_uint16(
                                Config().get_config_param('Main','DefaultDestinationPort'))
        self.protocol = ParseFormats.parse_uint8( Config().get_config_param('Main','DefaultProtocol'))
        self.life_time = ParseFormats.parse_uint8( Config().get_config_param('Main','LifeTime'))

        self.logger.debug("ending _load_main_data auction client")

    def _initialize_managers(self):
        """
        Initializes managers used.
        :return:
        """
        self.logger.debug("Starting _initialize_managers")
        self.auction_manager = AuctionManager(self.domain)
        self.bidding_object_manager = BiddingObjectManager()
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
                call = self.loop.call_at(when, self.handle_activate_resource_request_interval, start, ret_start[start], when)
                self._add_pending_tasks(ret_start[start].get_key(), call, when)

            for stop in ret_stop:
                when = self._calculate_when(stop)
                call = self.loop.call_at(when, self.handle_remove_resource_request_interval, stop, ret_stop[stop], when)
                self._add_pending_tasks(ret_stop[stop].get_key(), call, when)

        self.logger.debug("Ending _load_resources_request")

    def handle_activate_resource_request_interval(self, start:datetime,
                                         resource_request: ResourceRequest, when: float):
        self.logger.debug("start handle activate resource request interval")

        try:
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
            session = None
            if self.use_ipv6:
                session = self.auction_session_manager.create_agent_session(self.ip_address6, self.destination_address6,
                                 self.source_port, self.destination_port, self.protocol, self.life_time)
            else:
                session = self.auction_session_manager.create_agent_session(self.ip_address4, self.destination_address4,
                                 self.source_port, self.destination_port, self.protocol, self.life_time)

            # Gets the new message id
            message_id = session.get_next_message_id()
            message.set_seqno(message_id)
            message.set_ackseqno(0)
            session.set_resource_request(resource_request)
            session.set_start(interval.start)
            session.set_stop(interval.stop)

            # Sends the message to destination
            self.handle_send_message(message)

            # Add the session in the session container
            session.add_pending_message(message)
            self.auction_session_manager.add_session(session)

            # Assign the new session to the interval.
            interval.session = session.get_key()
        except Exception as e:
            self.logger.error('Error during handle activate resource request - Error: {0}'.format(str(e)))

        self.logger.debug('ending handle activate resource request interval')

    def handle_remove_resource_request_interval(self, stop:datetime,
                                         resource_request: ResourceRequest, when: float):
        """

        :param stop:
        :param resource_request:
        :param when:
        :return:
        """
        self.logger.debug('start handle activate resource request interval')
        try:
            # The task is no longer scheduled.
            self._remove_pending_task(resource_request.get_key(), when)


            interval = resource_request.get_interval_by_end_time(stop)

             # Gets the  auctions corresponding with this resource request interval
            session_id = interval.session

            session = self.auction_session_manager.get_session(session_id)

            auctions = session.get_auctions()

            # Teardowns the session created.
            self.handle_send_teardown_message()

            # Deletes active request process associated with this request interval.
            resource_request_process_ids = interval.get_resource_request_process()
            for resurce_request_process_id in resource_request_process_ids:
                self.agent_processor.delete_request(resurce_request_process_id)

            # deletes the reference to the auction (a session is not referencing it anymore)
            auctions_to_remove = self.auction_manager.decrement_references(auctions,session_id)
            for auction in auctions:
                self.handle_remove_auction(auction)

        except Exception as e:
            self.logger.error('Error during activate resource request interval - Error:{0}'.format(str(e)))

        self.logger.debug('ending handle activate resource request interval')

    def run(self):
        """
        Runs the application.
        :return:
        """
        self.source_port = random.randint(1024, 65000)
        if self.use_ipv6:
            print(self.ip_address6, self.source_port)
            run_app(self.app, host=str(self.ip_address6), port=self.source_port)
        else:
            print(self.ip_address4, self.source_port)
            run_app(self.app, host=str(self.ip_address4), port=self.source_port)


if __name__ == '__main__':
    try:
        agent = AuctionClient()
        agent.run()
    finally:
        print('closing event loop')
        agent.loop.close()