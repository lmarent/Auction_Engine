from datetime import datetime

from auction_client.resource_request import ResourceRequest
from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.client_main_data import ClientMainData
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.agent_processor import AgentProcessor
from auction_client.auction_session import AuctionSession
from auction_client.client_message_processor import ClientMessageProcessor

from foundation.auction_task import ScheduledTask
from foundation.auction_task import PeriodicTask
from foundation.config import Config
from foundation.auction_manager import AuctionManager
from foundation.session import SessionState

from python_wrapper.ipap_message import IpapMessage
from utils.auction_utils import log


class HandleAddResourceRequest(ScheduledTask):
    """
    Handle a new resource request. It parsers, adds and triggers the activation of the resource request.
    """

    def __init__(self, file_name: str, seconds_to_start: float):
        super(HandleAddResourceRequest, self).__init__(seconds_to_start)
        self.config = Config().get_config()
        self.file_name = file_name
        self.client_data = ClientMainData()
        self.resource_request_manager = ResourceRequestManager(self.client_data.domain)
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        self.logger.debug('starting run HandleAddResourceRequest')
        resource_requests = self.resource_request_manager.parse_resource_request_from_file(self.file_name)
        for resource_request in resource_requests:
            ret_start, ret_stop = self.resource_request_manager.add_resource_request(resource_request)
            for start in ret_start:
                when = self._calculate_when(start)
                activate_resource_request_int = HandleActivateResourceRequestInterval(start, ret_start[start], when)
                resource_request.add_task(activate_resource_request_int)
                activate_resource_request_int.start()

            for stop in ret_stop:
                when = self._calculate_when(stop)
                stop_resource_request_int = HandleRemoveResourceRequestInterval(stop, ret_stop[stop], when)
                resource_request.add_task(stop_resource_request_int)
                stop_resource_request_int.start()
        self.logger.debug('Ending run HandleAddResourceRequest')


class HandleActivateResourceRequestInterval(ScheduledTask):

    def __init__(self, start_datetime: datetime, resource_request: ResourceRequest, seconds_to_start: float):
        """
        Method to create the task
        :param start_datetime: date and time when the task should start
        :param seconds_to_start: seconds for starting the task.
        :param resource_request: resource request that should be started.
        """
        super(HandleActivateResourceRequestInterval, self).__init__(seconds_to_start)
        self.start_datetime = start_datetime
        self.resource_request = resource_request
        self.seconds_to_start = seconds_to_start
        self.client_data = ClientMainData()
        self.auction_session_manager = AuctionSessionManager()
        self.resource_request_manager = ResourceRequestManager(domain=self.client_data.domain)
        self.client_message_processor = ClientMessageProcessor()
        self.logger = log().get_logger()

    async def _run_specific(self):
        """
        Handles the activation of a resource request interval.
        :return:
        """
        self.logger.debug("starting to run HandleActivateResourceRequestInterval")
        try:
            # for now we request to any resource,
            # a protocol to spread resources available must be implemented
            resource_id = "ANY"
            interval = self.resource_request.get_interval_by_start_time(self.start_datetime)

            # Gets an ask message for the resource
            message = self.resource_request_manager.get_ipap_message(self.resource_request,
                                                                     self.start_datetime, resource_id,
                                                                     self.client_data.use_ipv6,
                                                                     str(self.client_data.ip_address4),
                                                                     str(self.client_data.ip_address6),
                                                                     self.client_data.source_port)

            # Create a new session for sending the request
            session = await self.client_message_processor.connect()

            # Gets the new message id
            message_id = session.get_next_message_id()
            message.set_seqno(message_id)
            message.set_ack_seq_no(0)
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

        self.logger.debug("ending to run HandleActivateResourceRequestInterval")


class HandleRemoveResourceRequestInterval(ScheduledTask):


    def __init__(self, stop_datetime: datetime, resource_request: ResourceRequest, seconds_to_start: float):
        """
        Method to create the task remove resource request interval
        :param stop_datetime: date and time when the resource request interval should be removed.
        :param resource_request: resource request that should be started.
        :param seconds_to_start: seconds for starting the task.
        """
        super(HandleRemoveResourceRequestInterval, self).__init__(seconds_to_start)
        self.stop_datetime = stop_datetime
        self.resource_request = resource_request
        self.seconds_to_start = seconds_to_start
        self.client_data = ClientMainData()
        self.auction_session_manager = AuctionSessionManager()
        self.agent_processor = AgentProcessor(self.client_data.domain, "")
        self.auction_manager = AuctionManager(self.client_data.domain)
        self.logger = log().get_logger()

    async def _run_specific(self):
        """
        Handles the removal of a resource request interval.
        """
        try:
            interval = self.resource_request.get_interval_by_end_time(self.stop_datetime)

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
            auctions_to_remove = self.auction_manager.decrement_references(auctions, session_id)
            for auction in auctions_to_remove:
                self.handle_remove_auction(auction)

        except Exception as e:
            self.logger.error('Error during activate resource request interval - Error:{0}'.format(str(e)))


class HandleAuctionMessage(ScheduledTask):
    def __init__(self, session: AuctionSession, ipap_message: IpapMessage, seconds_to_start: float):
        super(HandleAuctionMessage, self).__init__(seconds_to_start)
        self.session = session
        self.message = ipap_message
        self.logger = log().get_logger()

    def _run_specific(self):
        type = self.ipap_message.get_type()

        # TODO: Complete this code
        # if type == auction:
        #
        # elif type == bidding_object:
        #
        # elif type == allocation:
        #
        # else:
        #    logger.error("invalid type")


class HandleActivateSession(ScheduledTask):

    def __init__(self, seconds_to_start: float, session_key: str):
        super(HandleActivateSession, self).__init__(seconds_to_start)
        self.session_key = session_key
        self.auction_session_manager = AuctionSessionManager()
        self.logger = log().get_logger()

    def _run_specific(self):
        session = self.auction_session_manager.get_session(self.session_key)
        session.set_state(SessionState.SS_ACTIVE)


class HandleAuctionExecution(PeriodicTask):

    def __init__(self):
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        pass


class HandleAuctionRemove(ScheduledTask):

    def __init__(self):
        pass

    async def _run_specific(self, **kwargs):
        pass


# class HandledAddGenerateBiddingObject(ScheduledTask):
#
#     def __init__(self):
#         pass
#
#     async def _run_specific(self, **kwargs):
#         bidding_manager = app.get_bidding_object_manager()
#         for bidding_object in bidding_objects:
#             bidding_manager.add_bidding_object(bidding_object, loop)
#         pass


# class HandleActivateBiddingObject(ScheduledTask):
#
#     def __init__(self):
#         pass
#
#     async def _run_specific(self, **kwargs):
#         for bidding_object in bidding_objects:
#             bidding_object.activate(loop)


# class HandleSendBiddingObject(ScheduledTask):
#
#     def __init__(self):
#         pass
#
#     async def _run_specific(self, **kwargs):
#         for bidding_object in bidding_objects:
#             auction = bidding_object.get_auction()
#             mid = session.get_next_message_id()
#             message = get_message_bidding_object(mid, bidding_object)
#             session.add_pending_message(message)
#             loop.call_soon(functools.partial(handle_send_message, message, loop))
#

# class HandleRemoveBiddingObject(ScheduledTask):
#
#     def __init__(self):
#         pass
#
#     async def _run_specific(self, **kwargs):
#         bidding_object_manager = app.get_bidding_object_manager()
#         for bidding_object in bidding_objects:
#             bidding_object_manager.del_bidding_object(bidding_object)


# class HandleActivateAuction(ScheduledTask):
#
#     def __init__(self):
#         pass
#
#     async def _run_specific(self, **kwargs):
#         for auction in auctions:
#             auction.activate(loop)


class HandleRemoveAuction(ScheduledTask):

    def __init__(self, auctions: list):
        """

        :param auctions: List of auctions to remove.
        """
        self.client_data = ClientMainData()
        self.auction_manager = AuctionManager(self.client_data.domain)
        self.auctions = auctions
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        for auction in self.auctions:
            # remove from processing the auction
            # TODO: Remove from procesing.

            # delete all binding objects related with the auction
            # TODO: remove binding objects

            self.auction_manager.del_auction(auction)
