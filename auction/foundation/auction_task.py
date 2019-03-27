import asyncio
from contextlib import suppress
from abc import ABC
from abc import abstractmethod
from utils.auction_utils import log

class AuctionTask(ABC):
    """
    Represents a task to be executed for an auction bidding object.

    """

    def __init__(self, time: float):
        self.time = time
        self.is_started = False
        self._task = None
        self.logger = log().get_logger()

    def start(self):
        if not self.is_started:
            self.logger.debug("Starting {0}".format(type(self).__name__))
            self.is_started = True
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.is_started:
            self.logger.debug("Stopping {0}".format(type(self).__name__))
            self.is_started = False

            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    @abstractmethod
    async def _run(self):
        """
        Method for executing the tasks, first wait the scheduled time and then
        executes the task.
        """
        pass


class ScheduledTask(AuctionTask):
    """
    A single execution task to be executed in the future for an auctioning object

    It implements the observer pattern to inform observers about the task's ending.
    """
    def __init__(self, time: float):
        super(ScheduledTask, self).__init__(time)
        self._observers = []

    async def reschedule(self, time: float):
        """
        reschedule the task givin it the new time to wait until its activation
        :param time:
        :return:
        """
        await self.stop()
        self.time = time
        if self.is_started:
            self._task = asyncio.ensure_future(self._run())

    def attach(self, observer):
        """
        Attach an observer

        :param observer: Observer to include
        :return:
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """
        Removes an observer from the list

        :param observer: observer to remove
        :return:
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self):
        """
        Notify the tasks ending to observers.

        :return:
        """
        for observer in self._observers:
            observer.remove_task(self)

    @abstractmethod
    async def _run_specific(self):
        """
        To be overwritten with the actual logic to execute within the task
        :return:
        """
        pass

    async def _run(self):
        """
        Method for executing the tasks, first wait the scheduled time and then
        executes the task.
        """
        await asyncio.sleep(self.time)
        self.logger.debug("processing {0}".format(type(self).__name__))
        await self._run_specific()
        self.logger.debug("ending process for {0}".format(type(self).__name__))
        self.notify()


class PeriodicTask(AuctionTask):
    """
    A Periodic Task to be executed for an auctioning object
    """

    @abstractmethod
    async def _run_specific(self):
        """
        To be overwritten with the actual logic to execute within the task
        """
        pass

    async def _run(self):
        """
        Method for executing the tasks. First, it waits the scheduled time and then
        executes the task. After that execution, it waits again and continues like so
        until it is stopped.
        """
        while True:
            await asyncio.sleep(self.time)
            self.logger.debug("starting {0}".format(type(self).__name__))
            await self._run_specific()
            self.logger.debug("ending {0}".format(type(self).__name__))
