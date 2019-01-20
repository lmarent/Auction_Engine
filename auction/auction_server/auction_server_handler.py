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

from auction_server.auction_processor import AuctionProcessor
from datetime import datetime


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
        super(HandleLoadResourcesFromFile, self).__init__(seconds_to_start)
        self.auction = auction
        self.start = start
        self.auction_processor = AuctionProcessor()

    def _run_specific(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        next_start = self.start + datetime.timedelta(seconds=self.auction.get_interval().interval)

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
        super(HandleLoadResourcesFromFile, self).__init__(seconds_to_start)
        self.auction = auction
        self.auction_processor = AuctionProcessor()

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
            stop = self.auction.get_stop()
            interval = self.auction.get_interval()

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
        self.resource_manager = ResourceManager()

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
        self.resource_manager = ResourceManager()
        self.action_manager = AuctionManager()
        self.domain = domain
        self.immediate_start = immediate_start

    async def _run_specific(self, file_name: str):
        """
        Handles auction loading from file.

        :param file_name: name of he auction xml file to load
        :return:
        """
        try:
            auction_file_parser = AuctionXmlFileParser(self.domain)
            auctions = auction_file_parser.parse(file_name)
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
                    removal_task = HandleRemoveAuction(auction=auction, seconds_to_start=0)
                    auction.add_task(removal_task)

                else:
                    self.logger.error("The auction with key {0} could not be added".format(auction.get_key()))
        except Exception as e:
            self.logger.error("An error occur during load actions - Error:{}".format(str(e)))



class HandleSessionRequest(ScheduledTask):
    """

    """

    def __init__(self, message: IpapMessage, session_key: str, sender_address: str, sender_port: int,
                  protocol: int, seconds_to_start: float):
        """

        :param seconds_to_start:
        """
        super(HandleSessionRequest, self).__init__(seconds_to_start)
        self.message = message
        self.auction_manager = AuctionManager()
        self.auction_processor = AuctionProcessor()
        self.field_manager = FieldDefManager()
        self.message_processor = MessageProcessor()
        self.session_key = session_key
        self.sender_address = sender_address
        self.sender_port = sender_port
        self.protocol = protocol

    def is_complete(self, session_info: dic):
        #TODO: Implement
        pass


    async def _run_specific(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        auctions = self.auction_processor.get_applicable_auctions(self.message)

        session_info = self.auction_processor.get_session_information(self.message)

        if self.is_complete(session_info):
            ip_version = session_info[FieldDefManager.get_field("ipversion")]
            if ip_version == 4:
                src_address = session_info[FieldDefManager.get_field("srcip")]
            else:
                src_address = session_info[FieldDefManager.get_field("srcipv6")]
            scr_port = session_info[FieldDefManager.get_field("srcport")]

        message_to_send = AuctionManager.get_ipap_message(auctions, )

        session = Session(session_id=self.session_key, sender_address=self.sender_address,
                          sender_port=self.sender_port, receiver_address=src_address,
                          receiver_port=scr_port, protocol=self.protocol)

        self.message_processor.send_message()


