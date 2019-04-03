# bidding_object.py
from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType
from foundation.config_param import ConfigParam
from foundation.interval import Interval
from foundation.parse_format import ParseFormats

from utils.auction_utils import log

from datetime import datetime


class BiddingObject(AuctioningObject):
    """
    This class respresents the bidding objects being interchanged between users and the auctionner. 
    A bidding object has two parts:
    
      1. A set of elements which establish a route description
      2. A set of options which establish the duration of the bidding object. 
    """

    def __init__(self, auction_key: str, bidding_object_key: str, object_type: AuctioningObjectType,
                 elements: dict, options: dict):

        assert (object_type == AuctioningObjectType.BID or object_type == AuctioningObjectType.ALLOCATION)
        super(BiddingObject, self).__init__(bidding_object_key, object_type)

        # elements and options whenever used should be sorted by key.
        self.elements = elements
        self.options = options
        self.parent_auction = auction_key
        self.session_key = None

    def get_auction_key(self):
        """
        Returns the auction parant key
        :return: key of the parent auction
        """
        return self.parent_auction

    def get_element(self, element_name):
        if element_name in self.elements.keys():
            return self.elements[element_name]
        else:
            raise ValueError('Element with name: {} was not found'.format(element_name))

    def get_option(self, option_name):
        if option_name in self.options.keys():
            return self.options[option_name]
        else:
            raise ValueError('Option with name: {} was not found'.format(option_name))

    def get_option_value(self, option_name: str, name: str) -> ConfigParam:
        """
         Get a value by name from the misc rule attributes

        :param option_name: record name where to find
        :param name: option name to return
        :return: config_param representing the option.
        """
        # Convert to lower case for comparison.
        name = name.lower()

        if option_name in self.options:
            field_list = self.options[option_name]
            if name in field_list:
                return field_list[name]
            else:
                raise ValueError("name was not found in config params")
        else:
            raise ValueError("record was not found in config params")

    def calculate_interval(self, option_name: str, last_stop: datetime) -> Interval:
        """
         Calculates the interval for a options record
        :param option_name for which we want to create the interval.
        :param last_stop datetime of the last stop for thebididng object.
        :return: Interval created for the option
        """
        duration = 0
        interval = Interval()

        fstart = self.get_option_value(option_name, "Start")
        fstop = self.get_option_value(option_name, "Stop")

        if fstart.value:
            interval.start = ParseFormats.parse_time(fstart.value)
            if not interval.start:
                raise ValueError("Invalid start time {0}".format(fstart.value))

        if fstop.value:
            interval.stop = ParseFormats.parse_time(fstop.value)
            if not interval.stop:
                raise ValueError("Invalid stop time {0}".format(fstart.value))

        # do we have a stop time defined that is in the past ?
        if interval.stop and interval.stop <= datetime.now():
            logger = log().get_logger()
            logger.debug("Bidding object running time is already over")

        if interval.start < datetime.now():
            # start late tasks immediately
            interval.start = datetime.now()

        interval.duration = (interval.stop - interval.start).total_seconds()
        return interval

    def set_session(self, session_key: str):
        """
        Sets the session to whom this bidding object belogs to.

        :param session_key:
        :return:
        """
        self.session_key = session_key

    def get_session(self) -> str:
        """
        Gets the session key
        :return:
        """
        return self.session_key