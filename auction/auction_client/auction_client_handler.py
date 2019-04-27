from datetime import datetime
from datetime import timedelta
from math import floor
from math import fmod
from typing import List

from auction_client.resource_request import ResourceRequest
from auction_client.resource_request_manager import ResourceRequestManager
from auction_client.client_main_data import ClientMainData
from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.auction_session import AuctionSession
from auction_client.agent_processor import AgentProcessor
from auction_client.client_message_processor import ClientMessageProcessor
from auction_client.server_connection import ServerConnection
from auction_client.agent_template_container_manager import AgentTemplateContainerManager
from auction_client.resource_request_interval import ResourceRequestInterval

from foundation.auction_task import ScheduledTask
from foundation.config import Config
from foundation.auction_manager import AuctionManager
from foundation.session import SessionState
from foundation.auction import Auction
from foundation.bidding_object_manager import BiddingObjectManager
from foundation.auctioning_object import AuctioningObjectState
from foundation.bidding_object import BiddingObject

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

    async def _run_specific(self, **kwargs):
        try:
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

        except Exception as e:
            self.logger.error(str(e))


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

    async def _run_specific(self):
        """
        Handles the activation of a resource request interval.
        :return:
        """
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

            if session is not None:
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

            else:
                self.logger.error("the session could not be established")

        except Exception as e:
            self.logger.error('Error during handle activate resource request - Error: {0}'.format(str(e)))
            if session:
                await self.client_message_processor.process_disconnect(session)
                try:
                    self.auction_session_manager.del_session(session.get_key())
                except ValueError:
                    pass


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
        self.client_message_processor = ClientMessageProcessor()

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
            await self.client_message_processor.process_disconnect(session)

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

    async def _run_specific(self):
        try:
            # if the message has a ack nbr, then confirm the message
            ack_seq_no = self.message.get_ackseqno()
            if ack_seq_no > 0:
                self.server_connection.get_auction_session().confirm_message(ack_seq_no)

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
                self.logger.error("invalid message type - types:{0}".format(ipap_message_type.__str__()))
        except Exception as e:
            self.logger.error(str(e))


class HandleAskResponseMessage(ScheduledTask):

    def __init__(self, server_connection: ServerConnection, message: IpapMessage, seconds_to_start: float):
        super(HandleAskResponseMessage, self).__init__(seconds_to_start)
        self.client_data = ClientMainData()
        self.server_connection = server_connection
        self.resource_request_interval: ResourceRequestInterval = \
            server_connection.get_auction_session().resource_request_interval
        self.message = message
        self.agent_template_container = AgentTemplateContainerManager()
        self.auction_manager = AuctionManager(self.client_data.domain)
        self.agent_processor = AgentProcessor(self.client_data.domain, '')
        self.template_container = None

    def get_template_container(self):
        """
        Gets the template container for the particular server.
        """
        self.logger.debug("starting get_template_container")
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

        self.logger.debug("ending get_template_container")

    def create_auctions(self, auctions: List[Auction]) -> int:
        """
        Creates the auctions answered by the server as being used to bid for the resource
        :param auctions:list of auctions
        :return: maximum duration interval.
        """
        self.logger.debug("starting create_auctions")
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
                val_interval = interval.interval
                if val_interval > 0:
                    duration = (auction.get_stop() - auction.get_start()).total_seconds()
                    bid_intervals = floor(duration / val_interval)
                    modulus = fmod(duration, val_interval)

                    # If the requested time is less than the minimal interval for the auction
                    # we have to request te minimal interval.
                    if modulus > 0:
                        new_stop = auction.get_start() + timedelta(interval.interval * (bid_intervals + 1))
                        auction.set_stop(new_stop)

                self.auction_manager.add_auction(auction)

            # Update the maximum interval for the auction.
            if max_interval < interval.interval:
                max_interval = interval.interval

        return max_interval

    def create_process_request(self, auctions: list, max_interval: int, server_domain: int):
        """

        :param auctions: list of auction to put to process
        :param max_interval: the auction with the maximal duration interval
        :return:
        """
        self.logger.debug("starting process request")
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
        resource_request_key = None
        for module_name in auctions_by_module:
            aucs = auctions_by_module[module_name]
            resource_request_key = None
            for auction in aucs:
                if first_time:
                    if max_interval > 0:

                        bid_intervals = floor((req_stop - req_start).total_seconds() / max_interval)
                        duration = max_interval * (bid_intervals + 1)
                        req_stop = req_start + timedelta(seconds=duration)

                        resource_request_key = self.agent_processor.add_request(
                            self.server_connection.get_auction_session().get_key(),
                            self.resource_request_interval.get_fields(),
                            auction, server_domain, req_start, req_stop)

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

    async def _run_specific(self):
        try:
            self.get_template_container()
            auctions = self.auction_manager.parse_ipap_message(self.message, self.template_container)
            max_interval = self.create_auctions(auctions)
            self.create_process_request(auctions, max_interval, self.message.get_domain())
            self.auction_manager.increment_references(auctions, self.server_connection.get_auction_session().get_key())
            self.server_connection.get_auction_session().set_auctions(auctions)
        except Exception as e:
            self.logger.error(str(e))


class HandleActivateSession(ScheduledTask):

    def __init__(self, seconds_to_start: float, session_key: str):
        super(HandleActivateSession, self).__init__(seconds_to_start)
        self.session_key = session_key
        self.auction_session_manager = AuctionSessionManager()

    async def _run_specific(self):
        try:
            session = self.auction_session_manager.get_session(self.session_key)
            session.set_state(SessionState.SS_ACTIVE)
        except Exception as e:
            self.logger.error(str(e))


class HandleRequestProcessExecution(ScheduledTask):

    def __init__(self, request_process_key: str, seconds_to_start: float):
        """
        Handles the execution of an auction

        :param request_process_key: request process key to execute.
        :param seconds_to_start: seconds to wait for running the task.
        """
        super(HandleRequestProcessExecution, self).__init__(seconds_to_start)
        self.request_process_key = request_process_key
        self.client_data = ClientMainData()
        self.agent_processor = AgentProcessor(self.client_data.domain, '')

    async def _run_specific(self, **kwargs):
        try:
            bids = self.agent_processor.execute_request(self.request_process_key)
            self.logger.info("new bids created - nbr: {0}".format(str(len(bids))))

            handle_add_generate_bidding_object = HandledAddGenerateBiddingObject(self.request_process_key, bids, 0)
            handle_add_generate_bidding_object.start()

        except Exception as e:
            self.logger.error(str(e))


class HandleRequestProcessRemove(ScheduledTask):

    def __init__(self, request_process_key: str, seconds_to_start: float):
        """
        Handles the execution of an auction

        :param request_process_key: request process key to remove.
        :param seconds_to_start: seconds to wait for running the task.
        """
        super(HandleRequestProcessRemove, self).__init__(seconds_to_start)
        self.request_process_key = request_process_key
        self.client_data = ClientMainData()
        self.agent_processor = AgentProcessor(self.client_data.domain, '')
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        try:
            self.agent_processor.delete_request(self.request_process_key)

        except Exception as e:
            self.logger.error(str(e))


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
        try:
            # remove from processing the auction
            # TODO: Remove from procesing.

            # delete all binding objects related with the auction
            # TODO: remove binding objects

            self.auction_manager.delete_auction(self.auction.get_key())

        except Exception as e:
            self.logger.error(str(e))


class HandledAddGenerateBiddingObject(ScheduledTask):

    def __init__(self,request_process_key: str, bidding_objects: List[BiddingObject], seconds_to_start: float):
        """
        Handles the generation of new bidding objects

        :param request_process_key: process key where the bidding objects have been generated
        :param bidding_objects: bidding object list to include
        :param seconds_to_start: seconds to wait for running the task.
        """
        super(HandledAddGenerateBiddingObject, self).__init__(seconds_to_start)
        self.request_process_key = request_process_key
        self.bidding_objects = bidding_objects
        self.client_data = ClientMainData()
        self.agent_processor = AgentProcessor(self.client_data.domain, '')
        self.auction_session_manager = AuctionSessionManager()
        self.auction_manager = AuctionManager(self.client_data.domain)
        self.agent_template_container = AgentTemplateContainerManager()
        self.bidding_manager = BiddingObjectManager(self.client_data.domain)
        self.message_processor = ClientMessageProcessor()

    async def _run_specific(self, **kwargs):
        try:
            # Inserts the objects in the bidding object container
            for bidding_object in self.bidding_objects:
                self.bidding_manager.add_bidding_object(bidding_object)
                i = 0
                num_options = len(bidding_object.options)
                for option_name in sorted(bidding_object.options.keys()):
                    interval = bidding_object.calculate_interval(option_name, last_stop)
                    when = (interval.start - datetime.now()).total_seconds()
                    handle_activate = HandleActivateBiddingObject(self.client_connection, bidding_object, when)
                    handle_activate.start()

                    if i < num_options - 1:
                        when = (interval.stop - datetime.now()).total_seconds()
                        handle_inactivate = HandleInactivateBiddingObject(self.client_connection, bidding_object, when)
                        handle_inactivate.start()
                    else:
                        when = (interval.stop - datetime.now()).total_seconds()
                        handle_inactivate = HandleRemoveBiddingObject(self.client_connection, bidding_object, when)
                        handle_inactivate.start()

                    last_stop = interval.stop
                    i= i + 1

            # Gets the server domain from the request process
            server_domain = self.agent_processor.get_server_domain(self.request_process_key)

            # Gets the session
            session_key = self.agent_processor.get_session_for_request(self.request_process_key)
            session : AuctionSession = self.auction_session_manager.get_session(session_key)

            # Builds and sends the message
            template_container = self.agent_template_container.get_template_container(server_domain)
            ipap_message = self.bidding_manager.get_ipap_message(self.bidding_objects, template_container)
            ipap_message.set_seqno(session.get_next_message_id())
            ipap_message.set_ack_seq_no(0)
            session.add_pending_message(ipap_message)
            await self.message_processor.send_message(session.get_server_connnection(),ipap_message.get_message())

        except Exception as e:
            self.logger.error(str(e))


class HandleActivateBiddingObject(ScheduledTask):
    """
    Handles the activate of a bidding object. When active the bidding object is included in the auction for bidding.
    """
    def __init__(self, bidding_object: BiddingObject, seconds_to_start: float):
        super(HandleActivateBiddingObject, self).__init__(seconds_to_start)
        self.bidding_object = bidding_object
        self.server_main_data = ClientMainData()
        self.auction_manager = AuctionManager(self.server_main_data.domain)

    async def _run_specific(self):
        try:
            auction = self.auction_manager.get_auction(self.bidding_object.get_parent_key())
            if auction.get_state() == AuctioningObjectState.ACTIVE:
                self.bidding_object.set_state(AuctioningObjectState.ACTIVE)
            else:
                raise ValueError("Auction {0} is not active".format(auction.get_key()))
        except Exception as e:
            self.logger.error(str(e))


class HandleInactivateBiddingObject(ScheduledTask):
    """
    Handles the removal of a bidding object from the auction process.
    """
    def __init__(self, bidding_object: BiddingObject, seconds_to_start: float):
        super(HandleInactivateBiddingObject, self).__init__(seconds_to_start)
        self.bidding_object = bidding_object
        self.server_main_data = ClientMainData()
        self.bidding_manager = BiddingObjectManager(self.server_main_data.domain)
        self.auction_manager = AuctionManager(self.server_main_data.domain)

    async def _run_specific(self):
        try:
            auction = self.auction_manager.get_auction(self.bidding_object.get_parent_key())
            if auction.get_state() == AuctioningObjectState.ACTIVE:
                self.bidding_object.set_state(AuctioningObjectState.SCHEDULED)
            else:
                raise ValueError("Auction {0} is not active".format(auction.get_key()))
        except Exception as e:
            self.logger.error(str(e))


class HandleRemoveBiddingObject(ScheduledTask):
    """
    Handles the removal of a bidding object. This removes the bidding object from the auction for bidding.
    """
    def __init__(self, bidding_object: BiddingObject, seconds_to_start: float):
        super(HandleRemoveBiddingObject, self).__init__(seconds_to_start)
        self.bidding_object = bidding_object
        self.server_main_data = ClientMainData()
        self.bidding_manager = BiddingObjectManager(self.server_main_data.domain)
        self.auction_manager = AuctionManager(self.server_main_data.domain)

    async def _run_specific(self):
        try:

            auction = self.auction_manager.get_auction(self.bidding_object.get_parent_key())
            if auction.get_state() == AuctioningObjectState.ACTIVE:
                self.bidding_manager.del_actioning_object(self.bidding_object.get_key())
            else:
                raise ValueError("Auction {0} is not active".format(auction.get_key()))

        except Exception as e:
            self.logger.error(str(e))


# class HandleActivateAuction(ScheduledTask):
#
#     def __init__(self):
#         pass
#
#     async def _run_specific(self, **kwargs):
#         for auction in auctions:
#             auction.activate(loop)
