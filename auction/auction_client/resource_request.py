# resource_request.py
from datetime import datetime
from foundation.auctioning_object import AuctioningObjectType
from foundation.auctioning_object import AuctioningObject
from foundation.field_value import FieldValue
from auction_client.resource_request_interval import ResourceRequestInterval


class ResourceRequest(AuctioningObject):
    """
    This class represents resource request from users to be purchased in the market.
    """

    def __init__(self, key, time_format):
        super(ResourceRequest, self).__init__(key, AuctioningObjectType.RESOURCE_REQUEST)
        self.field_values = {}
        self.intervals = []
        self.time_format = time_format

    def add_interval(self, interval: ResourceRequestInterval):
        """
        Adds an interval to the resource request
        """
        self.intervals.append(interval)

    def add_field_value(self, field_value: FieldValue):
        """
        Adds a field to the resource request
        """
        self.field_values[field_value.name] = field_value

    def get_interval_by_start_time(self, start: datetime) -> ResourceRequestInterval:
        """
        Returns the interval with start time equals to start
        :param start start datetime to find.
        :rtype: ResourceRequestInterval
        """
        for interval in self.intervals:
            if interval.start == start:
                return interval
        return None

    def get_interval_by_end_time(self, end: datetime) -> ResourceRequestInterval:
        """
        Returns the interval with stop time equals to end
        :param end end datetime to find.
        :rtype: ResourceRequestInterval
        """
        for interval in self.intervals:
            if interval.stop == end:
                return interval
        return None

    def get_intervals(self) -> list:
        """
        Returns all intervals associated with the resource request
        """
        return self.intervals
