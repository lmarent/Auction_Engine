from aiohttp.web import Application, run_app
import asyncio
import functools
import pathlib
import yaml
from datetime import datetime, timedelta
from asyncio.events import TimerHandle

from auction_server.auction_processor import AuctionProcessor

from foundation.resource import Resource
from foundation.auction_manager import AuctionManager
from foundation.session_manager import SessionManager
from foundation.resource_manager import ResourceManager
from foundation.config import Config
from foundation.parse_format import ParseFormats
from foundation.auction_file_parser import AuctionXmlFileParser
from foundation.auction import Auction
from foundation.auctioning_object import AuctioningObjectState
from foundation.interval import Interval


class AuctionServer:

    def __init__(self):
        try:
            self.config = Config('auction_server.yaml').get_config()

            self.domain = ParseFormats.parse_int(self.config['Main']['Domain'])
            self.immediate_start = ParseFormats.parse_bool(self.config['Main']['ImmediateStart'])
            self._pending_tasks_by_auction = {}

            self._load_ip_address()
            self._load_database_params()
            self._initialize_managers()
            self._initilize_processors()

            # Start Listening the web server application
            self.app = Application()
            self.loop = asyncio.get_event_loop()
            self._load_resources()
            self._load_auctions()
        except Exception as e:
            print ("Error during server initialization - message:", str(e) )

    def _load_ip_address(self):
        """
        Sets the ip addreess defined in the configuration file
        """
        use_ipv6 = self.config['Control']['UseIPv6']
        use_ipv6 = ParseFormats.parse_bool(use_ipv6)
        if use_ipv6:
            self.ip_address = ParseFormats.parse_ipaddress(self.config['Control']['LocalAddr-V6'])
        else:
            self.ip_address = ParseFormats.parse_ipaddress(self.config['Control']['LocalAddr-V4'])

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
#       self.bidding_object_manager = BiddingObjectManager()
        self.session_manager = SessionManager()
        self.resource_manager = ResourceManager(self.domain)

    def _initilize_processors(self):
        """
        Initialize processors used
        :return:
        """
        if 'AUMProcessor' in self.config:
            if 'ModuleDir' in self.config['AUMProcessor']:
                module_directory = self.config['AUMProcessor']['ModuleDir']
                self.auction_processor = AuctionProcessor(self.domain, module_directory)
            else:
                ValueError(
                    'Configuration file does not have {0} entry within {1}'.format('ModuleDir', 'AumProcessor'))
        else:
            raise ValueError('There should be a AUMProcessor option set in config file')

    def _add_pending_tasks(self, key:str, call: TimerHandle, when:float):
        """
        Adds a ending tasks to an auction identified by its key
        :param key: key of the auction
        :param call: the awaitable that was scheduled to execute.
        :return:
        """
        if key not in self._pending_tasks_by_auction:
            self._pending_tasks_by_auction[key] = {}

        self._pending_tasks_by_auction[key][when]= call

    def _remove_pending_task(self, key:str, when:float):
        """
        Removes a pending task for an auction key and scheduled at a specific time
        :param key:  auction key
        :param when: specific time when it was scheduled.
        :return:
        """
        if key in self._pending_tasks_by_auction:
            if when in self._pending_tasks_by_auction[key]:
                self._pending_tasks_by_auction[key].pop(when)

    def _load_resources(self):
        """
        Loads resources from file
        :return:
        """
        if 'ResourceFile' in self.config:
            base_dir = pathlib.Path(__file__).parent.parent
            resource_file = self.config['ResourceFile']
            resource_file = base_dir / 'config' / resource_file
            self.handle_load_resources(resource_file)
        else:
            raise ValueError("The Resource File ({}) configuration option does not exist!".format('ResourceFile'))

    def _load_auctions(self):
        """
        Loads auctions from file
        :return:
        """
        if 'AuctionFile' in self.config:
            auction_file = self.config['AuctionFile']
            base_dir = pathlib.Path(__file__).parent.parent
            auction_file = base_dir / 'xmls' / auction_file
            auction_file = str(auction_file)
            self.handle_load_auctions(auction_file)
        else:
            raise ValueError("The Auction File ({}) configuration option does not exist!".format('AuctionFile'))

    def handle_load_resources(self, file_name: str):
        """
        Handles adding the resources defined in the file given to the auction server.
        The file name includes the absolute path.
        """
        try:
            with open(file_name) as f:
                resource_sets = yaml.load(f)
                for resource_set in resource_sets:
                    for resource in resource_sets[resource_set]:
                        resource = Resource(resource_set.lower() + '.' + resource.lower())
                        self.resource_manager.add_auctioning_object(resource)
        except IOError as e:
            raise ValueError("Error opening file - Message:", str(e))

    def handle_load_auctions(self, file_name: str):
        """
        Handles auction loading from file.

        :param file_name: name of he auction xml file to load
        :return:
        """
        auction_file_parser = AuctionXmlFileParser(self.domain)
        auctions = auction_file_parser.parse(file_name)
        for auction in auctions:
            if self.resource_manager.verify_auction(auction):
                self.auction_manager.add_auction(auction)

                # Schedule auction activation
                if self.immediate_start:
                    when = self.loop.time()
                    self.loop.call_soon(functools.partial(self.handle_activate_auction, auction, when))
                else:
                    diff_start = auction.get_start() - datetime.now()
                    when = self.loop.time() + diff_start.total_seconds()
                    call = self.loop.call_at(when, self.handle_activate_auction, auction, when)
                    self._add_pending_tasks(auction.get_key(), call, when)
                # Schedule auction removal
                diff_stop = auction.get_stop() - datetime.now()
                when = self.loop.time() + diff_stop.total_seconds()
                call = self.loop.call_at(when, self.handle_remove_auction, auction, when)
                self._add_pending_tasks(auction.get_key(), call, when)
            else:
                print("The auction with key {0} could not be added".format(auction.get_key()))

    def handle_activate_auction(self, auction: Auction, when:float):
        print('starting handle activate auction')

        # The task is no longer scheduled.
        self._remove_pending_task(auction.get_key(), when)

        # creates the auction processor
        self.auction_processor.add_auction_process(auction)
        start = auction.get_start()
        stop = auction.get_stop()
        interval = auction.get_interval()
        diff_start = auction.get_start() - datetime.now()

        # Activates its execution
        when = self.loop.time() + diff_start.total_seconds()
        call = self.loop.call_at(when, self.handle_push_execution, auction, start, stop, interval, when)
        self._add_pending_tasks(auction.get_key(), call, when)

        # Change the state of all auctions to active
        auction.set_state(AuctioningObjectState.ACTIVE)
        print('ending handle activate auction')

    def handle_remove_auction(self, auction: Auction, when:float):
        print('starting handle remove auction')

        # The task is no longer scheduled.
        self._remove_pending_task(auction.get_key(), when)

        # Cancels all pending task scheduled for the auction
        for when in self._pending_tasks_by_auction[auction.get_key()]:
            call = self._pending_tasks_by_auction[auction.get_key()][when]
            call.cancel()

        self._pending_tasks_by_auction.pop(auction.get_key())

        print('ending handle remove auction')

    def handle_push_execution(self, auction: Auction, start: datetime, stop:datetime, interval:Interval, when:float):
        print('starting handle push execution')

        # The task is no longer scheduled.
        self._remove_pending_task(auction.get_key(), when)

        stop_tmp = start + timedelta(seconds=interval.interval)

        if stop_tmp > stop:
            stop_tmp = stop

        # execute the algorithm
        self.auction_processor.execute_auction(auction.get_key(),start, stop_tmp)

        if stop_tmp < stop:
            diff_stop_tmp = stop_tmp - datetime.now()
            when = self.loop.time() + diff_stop_tmp.total_seconds()
            call = self.loop.call_at(when, self.handle_push_execution, auction, stop_tmp, stop, interval, when)
            self._add_pending_tasks(auction.get_key(), call, when)

        print('interval:', interval.align)


        print('ending handle push execution')

    def run(self):
        """
        Runs the application.
        :return:
        """
        run_app(self.app)
