from aiohttp.web import Application
import asyncio
from asyncio.events import TimerHandle
from datetime import datetime

from foundation.parse_format import ParseFormats
from foundation.config import Config
from utils.auction_utils import get_logger

class Agent:

    def __init__(self):
        self._pending_tasks_by_auction = {}

        # Start Listening the web server application
        self.loop = asyncio.get_event_loop()
        self.app = Application(self.loop)

        # Gets the log file
        config = Config()
        log_file_name = config['DefaultLogFile']
        self.app['log'] = get_logger(log_file_name)


    def _add_pending_tasks(self, key: str, call: TimerHandle, when: float):
        """
        Adds a pending tasks for an auctioning object identified by its key
        :param key: key of the auctioning object
        :param call: the awaitable that was scheduled to execute.
        :return:
        """
        if key not in self._pending_tasks_by_auction:
            self._pending_tasks_by_auction[key] = {}

        self._pending_tasks_by_auction[key][when] = call

    def _remove_pending_task(self, key: str, when: float):
        """
        Removes a pending task for an auctioning object identified by key
        and scheduled at a specific time

        :param key:  auctioning object key
        :param when: specific time when it was scheduled.
        :return:
        """
        if key in self._pending_tasks_by_auction:
            if when in self._pending_tasks_by_auction[key]:
                self._pending_tasks_by_auction[key].pop(when)

    def _calculate_when(self, start: datetime) -> float:
        """
        Calculates the datetime of an event given the current loop time
        :param start: datetime when the event should start
        :return: time in milliseconds when we should start the new event
        """
        diff_start = start - datetime.now()
        when = self.loop.time() + diff_start.total_seconds()
        return when

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

