import yaml
from foundation.auction_task import ScheduledTask
from foundation.auction_task import PeriodicTask
from foundation.resource_manager import ResourceManager
from foundation.resource import Resource
from foundation.auction_file_parser import AuctionXmlFileParser
from foundation.auction_manager import AuctionManager
from foundation.auction import Auction
from foundation.auctioning_object import AuctioningObjectState
from foundation.session import Session
from foundation.field_def_manager import FieldDefManager

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainer

from auction_server.auction_processor import AuctionProcessor
from auction_server.auction_processor import AgentFieldSet
from auction_server.server_message_processor import ServerMessageProcessor
from auction_server.server_main_data import ServerMainData

from datetime import datetime
from datetime import timedelta


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

        except IOError as e:
            self.logger.error("Error opening file - Message: {0}".format(str(e)))
            raise ValueError("Error opening file - Message:", str(e))


class HandleLoadAuction(ScheduledTask):
    """
    Handles auction loading from file.

    """

    def __init__(self, file_name: str, seconds_to_start: float,
                 domain: int, immediate_start: bool):
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
        self.domain = domain
        self.immediate_start = immediate_start

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
                    auction.add_task(activate_task)

                    seconds_to_start = auction.get_stop() - datetime.now()
                    removal_task = HandleRemoveAuction(auction=auction, seconds_to_start=seconds_to_start)
                    auction.add_task(removal_task)

                else:
                    self.logger.error("The auction with key {0} could not be added".format(auction.get_key()))
        except Exception as e:
            self.logger.error("An error occur during load actions - Error:{}".format(str(e)))


class HandleSessionRequest(ScheduledTask):
    """
    Handles a session request from an agent.
    """

    def __init__(self, message: IpapMessage,
                 session_key: str, use_ipv6: bool,
                 sender_address: str, sender_port: int,
                 protocol: int, seconds_to_start: float):
        """

        :param seconds_to_start:
        """
        super(HandleSessionRequest, self).__init__(seconds_to_start)
        self.message = message
        self.server_main_data = ServerMainData()
        self.auction_manager = AuctionManager(self.server_main_data.domain)
        self.auction_processor = AuctionProcessor(self.server_main_data.domain)
        self.field_manager = FieldDefManager()
        self.message_processor = ServerMessageProcessor()
        self.template_container = IpapTemplateContainer()
        self.session_key = session_key
        self.use_ipv6 = use_ipv6
        self.sender_address = sender_address
        self.sender_port = sender_port
        self.protocol = protocol

    def is_complete(self, session_info: dict):
        """
        Establishes if the session info given as part of the message is complete.

        :param session_info: session information given.
        :return: true or false
        """
        return len(session_info) == self.auction_processor.get_set_field(
            AgentFieldSet.SESSION_FIELD_SET_NAME)

    async def _run_specific(self):
        """
        Handles a session request from an agent.
        """
        auctions = self.auction_processor.get_applicable_auctions(self.message)
        session_info = self.auction_processor.get_session_information(self.message)

        if self.is_complete(session_info):
            field_ip_version = self.field_manager.get_field('ipversion')
            ip_version = session_info[field_ip_version]

            field_scrip = self.field_manager.get_field('srcip')
            src_address = session_info[field_scrip]

            if ip_version == 6:
                field_srcipv6 = self.field_manager.get_field('srcipv6')
                src_address = session_info[field_srcipv6]

            field_scr_port = self.field_manager.get_field('srcport')
            scr_port = session_info[field_scr_port]

            message_to_send = self.auction_manager.get_ipap_message(auctions, self.template_container,
                                                              self.sender_address,
                                                              self.sender_port)

            session = Session(session_id=self.session_key, sender_address=self.sender_address,
                              sender_port=self.sender_port, receiver_address=src_address,
                              receiver_port=scr_port, protocol=self.protocol)

            await self.message_processor.send_message_to_session(self.session_key, message_to_send.get_message())
        else:
            # TODO GENERATE AN ERROR.
            pass


class HandleAuctionMessage(ScheduledTask):
    def __init__(self, session: Session, ipap_message: IpapMessage, seconds_to_start: float):
        super(HandleAuctionMessage, self).__init__(seconds_to_start)
        self.session = session
        self.message = ipap_message

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
