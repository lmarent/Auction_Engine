# bidding_object.py
from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType
from foundation.config_param import ConfigParam
from foundation.interval import Interval
from foundation.parse_format import ParseFormats

from utils.auction_utils import log

from datetime import datetime
from asyncpg import Connection

class BiddingObject(AuctioningObject):
    """
    This class respresents the bidding objects being interchanged between users and the auctionner. 
    A bidding object has two parts:
    
      1. A set of elements which establish a route description
      2. A set of options which establish the duration of the bidding object. 
    """
    sql_hdr_insert = """INSERT INTO bidding_object_hdr( parent_key, key, session_id, bidding_object_type, 
                        bidding_object_status) VALUES ($1, $2, $3, $4, $5 )"""

    sql_element_insert = """INSERT INTO bidding_object_element( parent_key, key, element_name) VALUES ($1, $2, $3 )"""

    sql_option_insert =  """INSERT INTO bidding_object_option(parent_key, key, option_name) VALUES ($1, $2, $3 )"""

    sql_element_field_insert = """INSERT INTO bidding_object_element_field(parent_key, key, element_name, field_name, 
                                   field_type, value) VALUES ($1, $2, $3, $4, $5, $6)"""

    sql_option_field_insert = """INSERT INTO bidding_object_option_field(parent_key, key, option_name, field_name, 
                                   field_type, value) VALUES ($1, $2, $3, $4, $5, $6)"""

    def __init__(self, parent_key: str, bidding_object_key: str, object_type: AuctioningObjectType,
                 elements: dict, options: dict):

        assert (object_type == AuctioningObjectType.BID or object_type == AuctioningObjectType.ALLOCATION)
        super(BiddingObject, self).__init__(bidding_object_key, object_type)

        # elements and options whenever used should be sorted by key.
        self.elements = elements
        self.options = options
        self.parent_key = parent_key
        self.session_key = None
        self.participating_auction_processes = []

    def get_parent_key(self):
        """
        Returns the bidding object parent's key
        :return: key of the parent for bids it is an auction, for allocations it is a bid.
        """
        return self.parent_key

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

    def associate_auction_process(self, auction_process_key: str):
        """
        Attaches the bidding object to an auction process

        :param auction_process_key: auction process key for which the bidding object will be attached.
        :return:
        """
        self.participating_auction_processes.append(auction_process_key)

    def disassociate_auction_process(self, auction_process_key: str):
        """
        Detaches the bidding object from an auction process

        :param auction_process_key: auction process key for which the bidding object will be detached.
        :return:
        """
        self.participating_auction_processes.remove(auction_process_key)

    def get_participating_auction_processes(self) -> list:
        """
        gets the auction processes in which the bidding object is attached
        :return:
        """
        return self.participating_auction_processes

    def get_session(self) -> str:
        """
        Gets the session key
        :return:
        """
        return self.session_key

    async def store(self, connection: Connection):
        """
        stores the bidding object in the database
        :param connection: connection to the database
        :return:
        """
        async with connection.transaction():
            await connection.execute(BiddingObject.sql_hdr_insert, self.get_parent_key(), self.get_key(),
                        self.get_session(), self.get_type().value, self.get_state().value)

            # Insert the elements within the bidding object
            for element_name in self.elements:
                await connection.execute(BiddingObject.sql_element_insert,
                                   self.get_parent_key(), self.get_key(), element_name)
                for field_name in self.elements[element_name]:
                    config_param: ConfigParam = self.elements[element_name][field_name]
                    await connection.execute(BiddingObject.sql_element_field_insert,
                                             self.get_parent_key(), self.get_key(),
                                             element_name, field_name, config_param.get_type().value,
                                             config_param.get_value())

            # Inserts the option within the bidding object
            for option_name in self.options:
                await connection.execute(BiddingObject.sql_option_insert, self.get_parent_key(),
                                         self.get_key(), option_name)

                for field_name in self.options[option_name]:
                    config_param: ConfigParam = self.options[option_name][field_name]
                    await connection.execute(BiddingObject.sql_option_field_insert,
                                             self.get_parent_key(), self.get_key(), option_name,
                                             field_name, config_param.get_type().value, config_param.get_value())
