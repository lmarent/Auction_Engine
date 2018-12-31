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

            self._load_main_data()
            self._load_control_data()
            self._load_database_params()
            self._initialize_managers()
            self._initilize_processors()

            super(AuctionClient, self).__init__()

            self._load_resources_request()

        except Exception as e:
            print ("Error during server initialization - message:", str(e) )

    def _load_main_data(self):
        """
        Sets the main data defined in the configuration file
        """
        use_ipv6 = self.config['Main']['UseIPv6']
        self.use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if self.use_ipv6:
            self.ip_address6 = ParseFormats.parse_ipaddress(self.config['Main']['LocalAddr-V6'])
            self.destination_address6 = ParseFormats.parse_ipaddress(self.config['Main']['DefaultDestinationAddr-V6'])
        else:
            self.ip_address4 = ParseFormats.parse_ipaddress(self.config['Main']['LocalAddr-V4'])
            self.destination_address4 = ParseFormats.parse_ipaddress(self.config['Main']['DefaultDestinationAddr-V4'])

        # Gets default ports (origin, destination)
        self.source_port = ParseFormats.parse_uint16(self.config['Main']['DefaultSourcePort'])
        self.destination_port = ParseFormats.parse_uint16(self.config['Main']['DefaultDestinationPort'])
        self.protocol = ParseFormats.parse_uint8(self.config['Main']['DefaultProtocol'])
        self.life_time = ParseFormats.parse_uint8(self.config['Main']['LifeTime'])

    def _load_control_data(self):
        """
        Sets the control data defined in the configuration file
        """
        try:
            self.use_ssl = ParseFormats.parse_bool(self.config['Control']['UseSSL'])
            self.control_port = ParseFormats.parse_uint16(self.config['Control']['ControlPort'])
            self.log_on_connect = ParseFormats.parse_bool(self.config['Control']['LogOnConnect'])
            self.log_command = ParseFormats.parse_bool(self.config['Control']['LogCommand'])
            self.control_hosts = self.config['Control']['Access']['Host']
            self.control_user, self.control_passwd = \
                        self.config['Control']['Access']['User'].split(':')

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
                call = self.loop.call_at(when, self.handle_activate_resource_request_interval, start, ret_start[start], when)
                self._add_pending_tasks(ret_start[start].get_key(), call, when)

            for stop in ret_stop:
                when = self._calculate_when(stop)
                call = self.loop.call_at(when, self.handle_remove_resource_request_interval, stop, ret_stop[stop], when)
                self._add_pending_tasks(ret_stop[stop].get_key(), call, when)
    :
    def handle_activate_resource_request_interval(self, start:datetime,
                                         resource_request: ResourceRequest, when: float):
        print('start handle activate resource request interval')

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
            print('Error during handle activate resource request - Error:', str(e))

        print('ending handle activate resource request interval')

    def handle_remove_resource_request_interval(self, stop:datetime,
                                         resource_request: ResourceRequest, when: float):
        """

        :param stop:
        :param resource_request:
        :param when:
        :return:
        """
        print('start handle activate resource request interval')
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
        set < int > requestProcs = interval->resourceProcesses;
        for ( set < int >::
            iterator
        it = requestProcs.begin();
        it != requestProcs.end();
        ++it){
            proc->delRequest(*it);
        }

            # deletes the reference to the auction (a session is not referencing it anymore)
            auctions_to_remove = self.auction_manager.decrement_references(auctions,session_id)
            for auction in auctions:
                self.handle_remove_auction(auction)


            else {
                log->elog(ch, "Could not find the session for the request" );
            }

        except Exception as e:
            print('Error during activate resource request interval - Error:', str(e))
        print('ending handle activate resource request interval')


    def handle_send_message(self):
        pass

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