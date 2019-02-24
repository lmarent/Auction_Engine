# auctioning_object.py

from enum import Enum
from foundation.auction_task import AuctionTask
from foundation.auction_task import ScheduledTask


class AuctioningObjectState(Enum):
    """
    States throughout which can pass the auctioning object.
    """
    NEW = 0
    VALID = 1
    SCHEDULED = 2
    ACTIVE = 3
    DONE = 4
    ERROR = 5


class AuctioningObjectType(Enum):
    """
    Types for the auctioning objects"
    """
    AUCTION = 0
    BID = 1
    RESOURCE = 2
    RESOURCE_REQUEST = 3
    ALLOCATION = 4


class AuctioningObject:
    """
    Defines common attributes and methods used for auctioning object. An auctioning object
    represents an abtract class of all objects  being exchanged in the auction.
    """

    def __init__(self, key, auctioning_object_type: AuctioningObjectType, state=AuctioningObjectState.NEW):
        self.key = key
        self.auctioning_object_type = auctioning_object_type
        self.state = state
        self.active_tasks = []

    def set_state(self, state: AuctioningObjectState):
        """
        Change the object's state.
        """
        self.state = state

    def get_state(self):
        """
        Return object's state.
        """
        return self.state

    def get_key(self):
        """
        Return object's key.
        """
        return self.key

    def get_type(self) -> AuctioningObjectType:
        """
        Returns the auction object type
        :return: AuctioningObjectType
        """
        return self.auctioning_object_type

    def add_task(self, auction_task: AuctionTask):
        """
        adds an auction task to the list of pending tasks.

        :param auction_task: auction task to add.
        :return:
        """
        self.active_tasks.append(auction_task)
        if isinstance(auction_task, ScheduledTask):
            auction_task.attach(self)

    def reschedule_task(self, task_name: str, time: float):
        """
        Reschedule tasks with name task_name

        :param task_name: task name to reschedule
        :param time: time when the task should start.
        :return:
        """
        for task in self.active_tasks:
            if isinstance(task, ScheduledTask):
                if task_name == task.__class__.__name__:
                    task.reschedule(time)

    def remove_task(self, auction_task: AuctionTask):
        """
        call back called when an auction task ends.

        :param auction_task: auction task finished.
        :return:
        """

        self.active_tasks.remove(auction_task)

    async def stop_tasks(self):
        """
        Stops all tasks scheduled for this auction object.

        :return:
        """
        while True:
            try:
                task = self.active_tasks.pop()
                await task.stop()
            except IndexError:
                break
