import functools
from datetime import datetime

from auction_client.resource_request import ResourceRequest
from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.client_main_data import ClientMainData
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.agent_processor import AgentProcessor

from foundation.auction_task import ScheduledTask
from foundation.auction_task import PeriodicTask
from foundation.config import Config
from foundation.auction_manager import AuctionManager

from python_wrapper.ipap_message import IpapMessage

class HandleAddResourceRequest(ScheduledTask):
    """
    Handle a new resource request. It parsers, adds and triggers the activation of the resource request.
    """
    def __init__(self, file_name: str, seconds_to_start: float):
        super(HandleActivateResourceRequestInterval, self).__init__(seconds_to_start)
        self.config = Config().get_config()
        self.file_name = file_name
        self.resource_request_manager = ResourceRequestManager()
        pass

    async def _run_specific(self, **kwargs):
        time_format = self.config.get_config_param('Main', 'TimeFormat')
        resource_request = ResourceRequest(time_format)
        resource_request.from_xml(self.filename)
        ret_start, ret_stop = self.resource_request_manager.add_resource_request(resource_request)
        for start in ret_start:
            when = self._calculate_when(start)
            activate_resource_request_int = HandleActivateResourceRequestInterval(start,ret_start[start], when)
            resource_request.add_task(activate_resource_request_int)

        for stop in ret_stop:
            when = self._calculate_when(stop)
            stop_resource_request_int = HandleRemoveResourceRequestInterval(stop, ret_stop[stop], when)
            resource_request.add_task(stop_resource_request_int)


class HandleActivateResourceRequestInterval(ScheduledTask):

    def __init__(self, start: datetime, resource_request: ResourceRequest, seconds_to_start: float):
        """
        Method to create the task
        :param start: date and time when the task should start
        :param seconds_to_start: seconds for starting the task.
        :param resource_request: resource request that should be started.
        """
        super(HandleActivateResourceRequestInterval, self).__init__(seconds_to_start)
        self.start = start
        self.resource_request = resource_request
        self.seconds_to_start = seconds_to_start
        self.client_data = ClientMainData()
        self.auction_session_manager = AuctionSessionManager()

    async def _run_specific(self):
        """
        Handles the activation of a resource request interval.
        :return:
        """
        try:
            # for now we request to any resource,
            # a protocol to spread resources available must be implemented
            resource_id = "ANY"
            interval = self.resource_request.get_interval_by_start_time(self.start)

            # Gets an ask message for the resource
            message = self.resource_request_manager.get_ipap_message(self.resource_request,
                                                                     self.start, resource_id,
                                                                     self.client_data.use_ipv6,
                                                                     self.client_data.ip_address4,
                                                                     self.client_data.ip_address6,
                                                                     self.client_data.port)

            # Create a new session for sending the request
            session = None
            if self.client_data.use_ipv6:
                session = self.auction_session_manager.create_agent_session(self.client_data.ip_address6,
                                                                            self.client_data.destination_address6,
                                                                            self.client_data.source_port,
                                                                            self.client_data.destination_port,
                                                                            self.client_data.protocol,
                                                                            self.client_data.life_time)
            else:
                session = self.auction_session_manager.create_agent_session(self.client_data.ip_address4,
                                                                            self.client_data.destination_address4,
                                                                            self.client_data.source_port,
                                                                            self.client_data.destination_port,
                                                                            self.client_data.protocol,
                                                                            self.client_data.life_time)

            # Gets the new message id
            message_id = session.get_next_message_id()
            message.set_seqno(message_id)
            message.set_ackseqno(0)
            session.set_resource_request(self.resource_request)
            session.set_start(interval.start)
            session.set_stop(interval.stop)

            # Sends the message to destination
            await self.handle_send_message(message)

            # Add the session in the session container
            session.add_pending_message(message)
            self.auction_session_manager.add_session(session)

            # Assign the new session to the interval.
            interval.session = session.get_key()
        except Exception as e:
            self.logger.error('Error during handle activate resource request - Error: {0}'.format(str(e)))


class HandleRemoveResourceRequestInterval(ScheduledTask):

    def __init__(self, stop:datetime, resource_request: ResourceRequest, seconds_to_start: float):

        super(HandleRemoveResourceRequestInterval, self).__init__(seconds_to_start)
        self.stop = stop
        self.resource_request = resource_request
        self.seconds_to_start = seconds_to_start
        self.client_data = ClientMainData()
        self.auction_session_manager = AuctionSessionManager()
        self.agent_processor = AgentProcessor()
        self.auction_manager = AuctionManager(self.client_data.domain)

    async def _run_specific(self):
        """
        Handles the removal of a resource request interval.
        """
        try:
            interval = self.resource_request.get_interval_by_end_time(self.stop)

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
            for auction in auctions_to_remove:
                self.handle_remove_auction(auction)

        except Exception as e:
            self.logger.error('Error during activate resource request interval - Error:{0}'.format(str(e)))

class HandleAuctionMessage(ScheduledTask):
    def __init__(self, session_key:str, ipap_message: IpapMessage, seconds_to_start: float):
        super(HandleActivateSession, self).__init__(seconds_to_start)
        self.session_key = session_key
        self.message = ipap_message
        self.session_manager = AuctionSessionManager()

    def _run_specific(self):
        session = self.session_manager.get_session(self.session_key)

        type = self.ipap_message.get_type()

        # TODO: Complete this code
        #if type == auction:
        #
        #elif type == bidding_object:
        #
        #elif type == allocation:
        #
        #else:
        #    logger.error("invalid type")


class HandleActivateSession(ScheduledTask):

    def __init__(self, seconds_to_start: float, session_key:str):
        super(HandleActivateSession, self).__init__(seconds_to_start)
        self.session_key = session_key

    def _run_specific(self):
        session_manager = app.get_session_manager()
        session = session_manager.get_session(session_key)
        session.set_state(SessionState.SS_ACTIVE)


class HandleAuctionExecution(PeriodicTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        pass


class HandleAuctionRemove(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        pass


class HandledAddGenerateBiddingObject(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        bidding_manager = app.get_bidding_object_manager()
        for bidding_object in bidding_objects:
            bidding_manager.add_bidding_object(bidding_object, loop)
        pass


class HandleActivateBiddingObject(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        for bidding_object in bidding_objects:
            bidding_object.activate(loop)


class HandleSendBiddingObject(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        for bidding_object in bidding_objects:
            auction = bidding_object.get_auction()
            mid = session.get_next_message_id()
            message = get_message_bidding_object(mid, bidding_object)
            session.add_pending_message(message)
            loop.call_soon(functools.partial(handle_send_message, message, loop))


class HandleRemoveBiddingObject(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        bidding_object_manager = app.get_bidding_object_manager()
        for bidding_object in bidding_objects:
            bidding_object_manager.del_bidding_object(bidding_object)


class HandleActivateAuction(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        for auction in auctions:
            auction.activate(loop)


class HandleRemoveAuction(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        auction_manager = app.get_auction_manager()
        for auction in auctions:

            # remove from processing the auction
            # TODO: Remove from procesing.

            # delete all binding objects related with the auction
            # TODO: remove binding objects

            auction_manager.del_auction(auction)


