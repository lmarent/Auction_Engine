import yaml
from foundation.auction_task import ScheduledTask
from foundation.auction_task import PeriodicTask
from foundation.resource_manager import ResourceManager
from foundation.resource import Resource
from foundation.auction_parser import AuctionXmlFileParser
from foundation.auction_manager import AuctionManager
from foundation.auction import Auction
from foundation.auctioning_object import AuctioningObjectState
from foundation.field_def_manager import FieldDefManager
from foundation.bidding_object_manager import BiddingObjectManager
from foundation.bidding_object import BiddingObject

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainerSingleton

from auction_server.auction_processor import AuctionProcessor
from auction_server.auction_processor import AgentFieldSet
from auction_server.server_message_processor import ServerMessageProcessor
from auction_server.server_message_processor import ClientConnection
from auction_server.server_main_data import ServerMainData

from datetime import datetime
from datetime import timedelta
from utils.auction_utils import log


class HandleAuctionExecution(PeriodicTask):
    """
    Executes an auction in the system
    """

    def __init__(self, auction: Auction, start: datetime, seconds_to_start: float):
        """
        Creates the task

        :param auction:  auction to activate
        :param start:
        :param seconds_to_start: seconds when the auction should be activate
        """
        super(HandleAuctionExecution, self).__init__(seconds_to_start)
        self.auction = auction
        self.start = start
        self.server_main_data = ServerMainData()
        self.auction_processor = AuctionProcessor(self.server_main_data.domain)
        self.logger = log().get_logger()

    def _run_specific(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        next_start = self.start + timedelta(seconds=self.auction.get_interval().interval)

        if next_start > self.auction.get_stop():
            next_start = self.auction.get_stop()

        # Executes the algorithm
        self.auction_processor.execute_auction(self.auction.get_key(), self.start, next_start)

        # The start for the next execution is now setup again.
        self.start = next_start


class HandleActivateAuction(ScheduledTask):
    """
    Activates an auction in the system
    """

    def __init__(self, auction: Auction, seconds_to_start: float):
        """
        Creates the task

        :param auction: auction to activate
        :param seconds_to_start: seconds when the auction should be activate
        """
        super(HandleActivateAuction, self).__init__(seconds_to_start)
        self.auction = auction
        self.server_main_data = ServerMainData()
        self.auction_processor = AuctionProcessor(self.server_main_data.domain)
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        """
        Activates an auction

        :param auction: auction to activate
        :param when: seconds when the auction should be activate
        """
        try:
            # creates the auction processor
            self.auction_processor.add_auction_process(self.auction)
            start = self.auction.get_start()

            # Activates its execution
            when = self.auction.get_start() - datetime.now()
            execution_task = HandleAuctionExecution(self.auction, start, when)
            self.auction.add_task(execution_task)

            # Change the state of all auctions to active
            self.auction.set_state(AuctioningObjectState.ACTIVE)

        except Exception as e:
            self.logger.error("Auction {0} could not be activated - \
                                error: {1}".format(self.auction.get_key(), str(e)))
        self.logger.debug('Ending handle activate auction')


class HandleRemoveAuction(ScheduledTask):

    def __init__(self, auction: Auction, seconds_to_start: float):
        """
        Method to create the task

        :param auction: auction to remove
        :param seconds_to_start: seconds for starting the task.
        """
        super(HandleRemoveAuction, self).__init__(seconds_to_start)
        self.auction = auction
        self.logger = log().get_logger()

    async def _run_specific(self, **kwargs):
        """
        Removes an auction from the system

        :param kwargs:
        :return:
        """
        # Cancels all pending task scheduled for the auction
        await self.auction.stop_tasks()


class HandleLoadResourcesFromFile(ScheduledTask):
    """
    Handles adding the resources defined in the file given to the auction server.
    """

    def __init__(self, file_name: str, seconds_to_start: float):
        """
        Method to create the task
        :param file_name: file name to load. The file name includes the absolute path.
        :param seconds_to_start: seconds for starting the task.
        """
        super(HandleLoadResourcesFromFile, self).__init__(seconds_to_start)
        self.file_name = file_name
        self.server_main_data = ServerMainData()
        self.resource_manager = ResourceManager(self.server_main_data.domain)
        self.logger = log().get_logger()

    async def _run_specific(self):
        """
        Handles adding the resources defined in the file given to the auction server.

        """
        try:
            with open(self.file_name) as f:
                resource_sets = yaml.load(f)
                for resource_set in resource_sets:
                    for resource in resource_sets[resource_set]:
                        resource = Resource(resource_set.lower() + '.' + resource.lower())
                        self.resource_manager.add_auctioning_object(resource)
                        self.logger.info("resource with key {0} added".format(resource.get_key()))
        except IOError as e:
            self.logger.error("Error opening file - Message: {0}".format(str(e)))
            raise ValueError("Error opening file - Message:", str(e))


class HandleLoadAuction(ScheduledTask):
    """
    Handles auction loading from file.

    """

    def __init__(self, file_name: str, seconds_to_start: float):
        """
        Method to create the task
        :param file_name: file name to load. The file name includes the absolute path.
        :param seconds_to_start: seconds for starting the task.
        """
        super(HandleLoadAuction, self).__init__(seconds_to_start)
        self.file_name = file_name
        self.server_main_data = ServerMainData()
        self.resource_manager = ResourceManager(self.server_main_data.domain)
        self.auction_manager = AuctionManager(self.server_main_data.domain)
        self.domain = self.server_main_data.domain
        self.immediate_start = self.server_main_data.inmediate_start
        self.logger = log().get_logger()

    async def _run_specific(self):
        """
        Handles auction loading from file.

        :return:
        """
        try:
            auction_file_parser = AuctionXmlFileParser(self.domain)
            auctions = auction_file_parser.parse(self.file_name)
            for auction in auctions:
                if self.resource_manager.verify_auction(auction):
                    self.auction_manager.add_auction(auction)

                    # Schedule auction activation
                    if self.immediate_start:
                        seconds_to_start = 0
                    else:
                        seconds_to_start = auction.get_start() - datetime.now()

                    activate_task = HandleActivateAuction(auction=auction, seconds_to_start=seconds_to_start)
                    activate_task.start()
                    auction.add_task(activate_task)

                    seconds_to_start = auction.get_stop() - datetime.now()
                    removal_task = HandleRemoveAuction(auction=auction, seconds_to_start=seconds_to_start)
                    removal_task.start()
                    auction.add_task(removal_task)

                    self.logger.info("auction with key {0} added".format(auction.get_key()))
                else:
                    self.logger.error("The auction with key {0} could not be added".format(auction.get_key()))
        except Exception as e:
            self.logger.error("An error occur during load actions - Error:{}".format(str(e)))


class HandleAskRequest(ScheduledTask):
    """
    Handles an ask request from an agent. This request is performed to get auctions applicable for a resource.
    """

    def __init__(self, client_connection: ClientConnection, message: IpapMessage, seconds_to_start: float):
        """

        :param seconds_to_start:
        """
        super(HandleAskRequest, self).__init__(seconds_to_start)
        self.client_connection = client_connection
        self.message = message
        self.server_main_data = ServerMainData()
        self.auction_manager = AuctionManager(self.server_main_data.domain)
        self.auction_processor = AuctionProcessor(self.server_main_data.domain)
        self.field_manager = FieldDefManager()
        self.message_processor = ServerMessageProcessor()
        self.template_container = IpapTemplateContainerSingleton()
        self.logger = log().get_logger()

    def is_complete(self, session_info: dict):
        """
        Establishes if the session info given as part of the message is complete.

        :param session_info: session information given.
        :return: true or false
        """
        agent_session_set = self.auction_processor.get_set_field(AgentFieldSet.SESSION_FIELD_SET_NAME)
        return len(session_info) == len(agent_session_set)

    async def _run_specific(self):
        """
        Handles a session request from an agent.
        """
        auctions = self.auction_processor.get_applicable_auctions(self.message)
        self.logger.debug("nuber of applicable auctions: {0}".format(len(auctions)))
        session_info = self.auction_processor.get_session_information(self.message)

        if self.server_main_data.use_ipv6:
            s_address = self.server_main_data.ip_address6.__str__()
        else:
            s_address = self.server_main_data.ip_address4.__str__()

        if self.is_complete(session_info):
            message_to_send = self.auction_manager.get_ipap_message(auctions, self.server_main_data.use_ipv6,
                                                                    s_address, self.server_main_data.local_port)
            message_to_send.set_ack_seq_no(self.message.get_seqno())
            message_to_send.set_seqno(self.client_connection.session.get_next_message_id())

            await self.message_processor.send_message(self.client_connection,
                                                                 message_to_send.get_message())
        else:
            ack_message = self.message_processor.build_ack_message(self.client_connection.session.get_next_message_id(),
                                                     self.message.get_seqno())
            await self.message_processor.send_message(self.client_connection,
                                                      ack_message.get_message())


class HandleActivateBiddingObject(ScheduledTask):
    """
    Handles the activate of a bidding object. When active the bidding object is included in the auction for bidding.
    """
    def __init__(self, client_connection: ClientConnection, bidding_object: BiddingObject, seconds_to_start: float):
        super(HandleActivateBiddingObject, self).__init__(seconds_to_start)
        self.client_connection = client_connection
        self.bidding_object = bidding_object
        self.server_main_data = ServerMainData()
        self.auction_manager = AuctionManager(self.server_main_data.domain)
        self.auction_processor = AuctionProcessor(self.server_main_data.domain)

    def _run_specific(self):
        auction = self.auction_manager.get_auction(self.bidding_object.get_auction_key())
        if auction.get_state() == AuctioningObjectState.ACTIVE:
            self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), self.bidding_object)
            self.bidding_object.set_state(AuctioningObjectState.ACTIVE)
        else:
            raise ValueError("Auction {0} is not active".format(auction.get_key()))


class HandleRemoveBiddingObject(ScheduledTask):
    """
    Handles the removal of a bidding object. This parte removes the bidding object from the auction for bidding.
    """
    def __init__(self, client_connection: ClientConnection, bidding_object: BiddingObject, seconds_to_start: float):
        super(HandleActivateBiddingObject, self).__init__(seconds_to_start)
        self.client_connection = client_connection
        self.bidding_object = bidding_object
        self.server_main_data = ServerMainData()
        self.bidding_manager = BiddingObjectManager(self.server_main_data.domain)
        self.auction_manager = AuctionManager(self.server_main_data.domain)
        self.auction_processor = AuctionProcessor(self.server_main_data.domain)

    def _run_specific(self):
        auction = self.auction_manager.get_auction(self.bidding_object.get_auction_key())
        if auction.get_state() == AuctioningObjectState.ACTIVE:
            self.auction_processor.delete_bidding_object_from_auction_process(auction.get_key(), self.bidding_object)
            self.bidding_manager.del_actioning_object(self.bidding_object.get_key())
        else:
            raise ValueError("Auction {0} is not active".format(auction.get_key()))


class HandleAddBiddingObjects(ScheduledTask):
    """
    This class handles adding a new bidding object sent from an agent to the server.
    """
    def __init__(self, client_connection: ClientConnection, ipap_message: IpapMessage, seconds_to_start: float):
        super(HandleAddBiddingObjects, self).__init__(seconds_to_start)
        self.client_connection = client_connection
        self.ipap_message = ipap_message
        self.server_main_data = ServerMainData()
        self.server_message_processor = ServerMessageProcessor()
        self.bididing_manager = BiddingObjectManager(self.server_main_data.domain)
        self.template_container = IpapTemplateContainerSingleton()
        self.logger = log().get_logger()

    def _run_specific(self):
        """
        Adds bidding objects sent from an agent.
        """
        self.logger.debug("starting HandleAddBiddingObjects")
        # parse the message
        bidding_objects = self.bididing_manager.parse_ipap_message(self.ipap_message, self.template_container)

        # insert bidding objects to bidding object manager
        session = self.client_connection.get_auction_session()
        last_stop = datetime.now()
        for bidding_object in bidding_objects:
            bidding_object.set_session(session.get_key())
            self.bididing_manager.add_auctioning_object(bidding_object)
            for option_name in sorted(bidding_object.options.iterkeys()):
                interval = bidding_object.calculate_interval(option_name, last_stop)
                handle_activate = HandleActivateBiddingObject()
                handle_activate.start()
                handle_remove = HandleRemoveBiddingObject()
                handle_remove.start()
                last_stop = interval.stop

        # confirm the message
        confim_message = self.server_message_processor.build_ack_message(session.get_next_message_id(),
                                                                         self.ipap_message.get_seqno() + 1)
        self.server_message_processor.send_message(self.client_connection, confim_message.get_message())
        self.logger.debug("ending HandleAddBiddingObjects")


class HandleAuctionMessage(ScheduledTask):
    def __init__(self, client_connection: ClientConnection, ipap_message: IpapMessage, seconds_to_start: float):
        super(HandleAuctionMessage, self).__init__(seconds_to_start)
        self.client_connection = client_connection
        self.message = ipap_message
        self.template_container = IpapTemplateContainerSingleton()
        self.logger = log().get_logger()

    def _run_specific(self):

        # if the message has a ack nbr, then confirm the message
        seq_no = self.message.get_seqno()
        ack_seq_no = self.message.get_ackseqno()
        if ack_seq_no >0:
            self.client_connection.session.confirm_message(ack_seq_no)

        ipap_message_type = self.message.get_types()
        if ipap_message_type.is_ask_message():
            handle_ask_request = HandleAskRequest(self.client_connection, self.message, 0)
            handle_ask_request.start()

        if ipap_message_type.is_auction_message():
            # TODO: It must implement new auctions.
            pass

        if ipap_message_type.is_bidding_message():
            handle_bidding_object_interaction = HandleAddBiddingObjects(self.client_connection, self.message, 0)
            handle_bidding_object_interaction.start()

        if ipap_message_type.is_allocation_message():
            # TODO: implement the code
            pass

        else:
            self.logger.error("invalid message type")
