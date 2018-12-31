from aiohttp.web import Application
import asyncio
from asyncio.events import TimerHandle
from datetime import datetime

from foundation.parse_format import ParseFormats

class Agent:

    def __init__(self):
        self._pending_tasks_by_auction = {}

        # Start Listening the web server application
        self.app = Application()
        self.loop = asyncio.get_event_loop()

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

    def _load_control_port(self):
        """
        Sets the control port defined in the configuration file
        :return:
        """
        s_port = self.config['Control']['ControlPort']
        self.port = ParseFormats.parse_int(s_port)
