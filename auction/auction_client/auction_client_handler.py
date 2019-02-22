from datetime import datetime
from math import floor
from math import fmod

from auction_client.resource_request import ResourceRequest
from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.client_main_data import ClientMainData
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.agent_processor import AgentProcessor
from auction_client.client_message_processor import ClientMessageProcessor
from auction_client.server_connection import ServerConnection
from auction_client.agent_template_container_manager import AgentTemplateContainerManager
from auction_client.resource_request_interval import ResourceRequestInterval

from foundation.auction_task import ScheduledTask
from foundation.auction_task import PeriodicTask
from foundation.config import Config
from foundation.auction_manager import AuctionManager
from foundation.session import SessionState
from foundation.auction import Auction

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainer
from utils.auction_utils import log
from utils.auction_utils import DateUtils


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
                when = DateUtils().calculate_when(start)
                activate_resource_request_int = HandleActivateResourceRequestInterval(start, ret_start[start], when)
                resource_request.add_task(activate_resource_request_int)
                activate_resource_request_int.start()

            for stop in ret_stop:
                when = DateUtils().calculate_when(stop)
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
        session = None
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

            session.set_resource_request_interval(interval)
            session.set_start(interval.start)
            session.set_stop(interval.stop)

            # Add the session in the session container
            self.auction_session_manager.add_session(session)

            # Add the pending message.
            session.add_pending_message(message)

            # Sends the message to destination
            await self.client_message_processor.send_message(session.get_server_connnection(),
                                                             message.get_message())

            # Assign the new session to the interval.
            interval.session = session.get_key()

        except Exception as e:
            self.logger.error('Error during handle activate resource request - Error: {0}'.format(str(e)))
            if session:
                self.client_message_processor.process_disconnect(session)
                try:
                    self.auction_session_manager.del_session(session.get_key())
                except ValueError:
                    pass

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
                handle_auction_remove = HandleAuctionRemove(auction, 0)
                handle_auction_remove.start()

        except Exception as e:
            self.logger.error('Error during activate resource request interval - Error:{0}'.format(str(e)))


class HandleAuctionMessage(ScheduledTask):
    def __init__(self, server_connection: ServerConnection, ipap_message: IpapMessage, seconds_to_start: float):
        super(HandleAuctionMessage, self).__init__(seconds_to_start)
        self.server_connection = server_connection
        self.message = ipap_message
        self.logger = log().get_logger()

    def _run_specific(self):
        # if the message has a ack nbr, then confirm the message
        seq_no = self.message.get_seqno()
        ack_seq_no = self.message.get_ackseqno()
        if ack_seq_no > 0:
            self.server_connection.session.confirm_message(ack_seq_no)

        ipap_message_type = self.message.get_types()
        if ipap_message_type.is_auction_message():
            ask_response_message = HandleAskResponseMessage(self.server_connection, self.message, 0)
            ask_response_message.start()

            pass

        if ipap_message_type.is_bidding_message():
            # TODO: implement the code
            pass

        if ipap_message_type.is_allocation_message():
            # TODO: implement the code
            pass

        else:
            self.logger.error("invalid message type")


class HandleAskResponseMessage(ScheduledTask):

    def __init__(self, server_connection: ServerConnection, message: IpapMessage, seconds_to_start: float):
        super(HandleAskResponseMessage, self).__init__(seconds_to_start)
        self.client_data = ClientMainData()
        self.server_connection = server_connection
        self.resource_request_interval: ResourceRequestInterval = server_connection.session.resource_request_interval
        self.message = message
        self.agent_template_container = AgentTemplateContainerManager()
        self.auction_manager = AuctionManager(self.client_data.domain)
        self.agent_processor = AgentProcessor(self.client_data.domain, None)
        self.template_container = None
        self.logger = log().get_logger()

    def get_template_container(self):
        """
        Gets the template container for the particular server.
        """
        domain = self.message.get_domain()
        if domain > 0:
            try:
                self.template_container = self.agent_template_container.get_template_container(domain)
            except ValueError:
                template_container = IpapTemplateContainer()
                self.agent_template_container.add_template_container(domain, template_container)
                self.template_container = template_container
        else:
            self.logger.error("Invalid domain id associated with the message")
            raise ValueError("Invalid domain id associated with the message")


    def create_auctions(self, auctions: list) -> int:
        """
        Creates the auctions answered by the server as being used to bid for the resource
        :param auctions:list of auctions
        :return: maximum duration inteval.
        """
        # This variable maintains the auction with the maximal duration interval, so
        # The request should last at least an interval multiple.
        max_interval = 0

        for auction in auctions:
            # search the auction in the auction container, if it exists then updates its intervals.
            try:
                auction2 = self.auction_manager.get_auction(auction.get_key())
                interval = auction2.get_interval()
                if auction2.get_start() > self.resource_request_interval.start:
                    auction2.set_start(self.resource_request_interval.start)

                if auction2.get_stop() < self.resource_request_interval.stop:
                    auction2.set_stop(self.resource_request_interval.stop)

                when = DateUtils().calculate_when(auction2.get_stop())
                auction2.reschedule_task(HandleAuctionRemove.__name__, when)

            except ValueError:
                # the auction does not exists, so we need to create a new auction process.
                interval = auction.get_interval()
                auction.intersect_interval(interval.start, interval.stop)
                if interval.interval > 0:
                    bid_intervals = floor((auction.get_stop() - auction.get_start()) / interval.interval)
                    modulus = fmod((auction.get_stop() - auction.get_start()), interval.interval)

                    # If the requested time is less than the minimal interval for the auction
                    # we have to request te minimal interval.
                    if modulus > 0:
                        new_stop = auction.get_start() + interval.interval * (bid_intervals + 1)
                        auction.set_stop(new_stop)

                self.auction_manager.add_auction(auction)

            # Update the maximum interval for the auction.
            if max_interval < interval.interval:
                max_interval = interval.interval

        return max_interval

    def create_process_request(self, auctions:list, max_interval: int):
        """

        :param auctions: list of auction to put to process
        :param max_interval: the auction with the maximal duration interval
        :return:
        """
        # Go through the list of auctions and create groups by their module
        auctions_by_module = {}

        for auction in auctions:
            module_name = auction.get_module_name()
            if module_name not in auctions_by_module:
                auctions_by_module[module_name] = []
            auctions_by_module[module_name].append(auction)
        req_start = self.resource_request_interval.start
        req_stop = self.resource_request_interval.stop

        first_time = True
        for module_name in auctions_by_module:
            aucs = auctions_by_module[module_name]
            resource_request_key = None
            for auction in aucs:
                if first_time:
                    if max_interval > 0:
                        bid_intervals = floor((req_stop -req_start)/ max_interval)
                        modulus = fmod((req_stop -req_start), max_interval)
                        duration = max_interval * (bid_intervals  + 1)
                        req_stop = req_start + duration

                        resource_request_key=self.agent_processor.add_request(self.server_connection.session.get_key(),
                                                     self.resource_request_interval.get_fields(),
                                                     auction, req_start, req_stop)
                    self.resource_request_interval.add_resource_request_process(resource_request_key)
                    first_time = False
                else:
                    self.agent_processor.add_auction_request(resource_request_key, auction)

        when = DateUtils.calculate_when(req_start)
        handle_request_process_execution = HandleRequestProcessExecution(resource_request_key, when)
        handle_request_process_execution.start()

        when = DateUtils.calculate_when(req_stop)
        handle_request_process_remove = HandleRequestProcessRemove(resource_request_key, when)
        handle_request_process_remove.start()

    def _run_specific(self):

        self.get_template_container()
        auctions = self.auction_manager.parse_ipap_message(self.message, self.template_container)
        max_interval = self.create_auctions(auctions)
        self.create_process_request(auctions, max_interval)
        self.auction_manager.increment_references(auctions, self.server_connection.session.get_key())
        self.server_connection.session.set_auctions(auctions)


class HandleActivateSession(ScheduledTask):

    def __init__(self, seconds_to_start: float, session_key: str):
        super(HandleActivateSession, self).__init__(seconds_to_start)
        self.session_key = session_key
        self.auction_session_manager = AuctionSessionManager()
        self.logger = log().get_logger()

    def _run_specific(self):
        session = self.auction_session_manager.get_session(self.session_key)
        session.set_state(SessionState.SS_ACTIVE)


class HandleRequestProcessExecution(ScheduledTask):

    def __init__(self, request_process_key:str, seconds_to_start: float):
        """
        Handles the execution of an auction

        :param auction: auction to execute.
        :param seconds_to_start: seconds to wait for running the task.
        """
        super(HandleRequestProcessExecution, self).__init__(seconds_to_start)
        self.request_process_key = request_process_key
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        pass

class HandleRequestProcessRemove(ScheduledTask):

    def __init__(self, request_process_key:str, seconds_to_start: float):
        """
        Handles the execution of an auction

        :param auction: auction to execute.
        :param seconds_to_start: seconds to wait for running the task.
        """
        super(HandleRequestProcessRemove, self).__init__(seconds_to_start)
        self.request_process_key = request_process_key
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        pass


class HandleAuctionRemove(ScheduledTask):

    def __init__(self, auction: Auction, seconds_to_start: float):
        """
        Handles the removal of an auction

        :param auction: auction to remove.
        :param seconds_to_start: seconds to wait for running the task.
        """
        super(HandleAuctionRemove, self).__init__(seconds_to_start)
        self.client_data = ClientMainData()
        self.auction_manager = AuctionManager(self.client_data.domain)
        self.auction = auction
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        # remove from processing the auction
        # TODO: Remove from procesing.

        # delete all binding objects related with the auction
        # TODO: remove binding objects

        self.auction_manager.del_auction(self.auction)


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

