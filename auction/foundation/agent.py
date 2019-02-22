from aiohttp.web import Application
import asyncio
from asyncio.events import TimerHandle
from datetime import datetime

from foundation.parse_format import ParseFormats
from foundation.config import Config

from utils.auction_utils import log
from abc import ABC
from abc import abstractmethod

class Agent(ABC):

    def __init__(self, config_file_name: str):
        self._pending_tasks_by_auction = {}

        self.config = Config(config_file_name).get_config()

        # Start Listening the web server application
        loop = asyncio.get_event_loop()
        self.app = Application(loop=loop)

        # Gets the log file
        log_file_name = self.config['DefaultLogFile']
        self.logger = log(log_file_name).get_logger()

        self.domain = ParseFormats.parse_int(Config().get_config_param('Main', 'Domain'))
        self.immediate_start = ParseFormats.parse_bool(Config().get_config_param('Main', 'ImmediateStart'))

        self._load_main_data()
        self._load_control_data()
        self._load_database_params()

    @abstractmethod
    def _load_main_data(self):
        pass

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

    def _load_control_data(self):
        """
        Sets the control data defined in the configuration file
        """
        self.logger.debug("Stating _load_control_data")

        try:
            self.use_ssl = ParseFormats.parse_bool(Config().get_config_param('Control','UseSSL'))
            self.control_port = ParseFormats.parse_uint16(Config().get_config_param('Control','ControlPort'))
            self.log_on_connect = ParseFormats.parse_bool(Config().get_config_param('Control','LogOnConnect'))
            self.log_command = ParseFormats.parse_bool(Config().get_config_param('Control','LogCommand'))
            self.control_hosts = self.config['Control']['Access']['Host']
            self.control_user, self.control_passwd = \
                self.config['Control']['Access']['User'].split(':')

            self.logger.debug("Ending _load_control_data")

        except ValueError as verr:
            self.logger.error("The value for control port{0} is not a valid number".format(
                Config().get_config_param('Control', 'ControlPort')))

            raise ValueError("The value for control port{0} is not a valid number".format(
                Config().get_config_param('Control', 'ControlPort')))

    def _load_database_params(self):
        """
        Loads the database parameters from configuration file
        """
        self.logger.debug("starting _load_database_params")

        self.db_name = Config().get_config_param('Postgres', 'Database')
        self.db_user = Config().get_config_param('Postgres', 'User')
        self.db_passwd = Config().get_config_param('Postgres', 'Password')
        self.db_ip_address = Config().get_config_param('Postgres', 'Host')
        self.db_port = ParseFormats.parse_uint16(Config().get_config_param('Postgres', 'Port'))

        self.logger.debug("ending _load_database_params")
