#resource_request.py
import datetime
from foundation.auctioning_object import AuctioningObject
from foundation.interval import Interval
import xml

class ResourceRequest(AuctioningObject):
    """
    This class represents resource request from users to be purchased in the market.
    """
    
    def __init__(self, time_format, quantity=0, unit_budget=0, max_value=0, dst_id=None, dst_port=0):
        super(ResourceRequest, self).__init__()
        self.quantity = quantity
        self.unit_budget = unit_budget
        self.max_value = max_value
        self.dst_id = dst_id
        self.dst_port = dst_port
        self.intervals = []
        self.time_format = time_format

    def add_interval(self, intervaL):
        """
        Adds an interval to the resource request
        """
        self.interval.append(interval)


    @staticmethod
    def parse_interval(interval, startatleast):

        start = startatleast
        sstart = interval.getElementsByTagName('Start')[0]
        sstop = interval.getElementsByTagName('Stop')[0]
        sdurantion = interval.getElementsByTagName('Duration')[0]
        sinterval = interval.getElementsByTagName('Interval')[0]
        salign = interval.getElementsByTagName('Align')[0]

        interval_dict = {
            'start' : sstart, 'stop' : sstop, 'duration' : sduration, 
            'interval' : sinterval, 'align' : salign 
            } 

        new_interval = Interval() 
        new_interval.parse_interval(interval_dict, startatleast)
        return new_interval.start, new_interval


    def from_xml(self, filename):
        try:
            BASE_DIR = pathlib.Path(__file__).parent.parent
            config_path = BASE_DIR / 'config' / filename
            DOMTree = xml.dom.minidom.parse(config_path)
            collection = DOMTree.documentElement

            resource_requests = collection.getElementsByTagName("RESOURCE_REQUEST")

            for resource_request in resource_requests:
                self.quantity = resource_request.getElementsByTagName('quantity')[0]
                self.unit_budget = resource_request.getElementsByTagName('unitbudget')[0]
                self.max_value = resource_request.getElementsByTagName('maxvalue')[0]
                self.dst_ip = resource_request.getElementsByTagName('dstIP')[0]
                self.dst_port = resource_request.getElementsByTagName('dstPort')[0]

                intervals = resource_request.getElementsByTagName('INTERVAL')
                start = datetime.datetime.now()
                for interval in intervals:
                    start, new_interval = self.parse_interval(interval, start)
                    self.intervals.append(new_interval)
        except Exception as exp:
            print ('exception occurs:', str(e))

    def get_interval_by_start_time(self, start):
        """
        Returns the interval with start time equals to start
        """
        for interval in self.intervals:
            if interval.start == start:
                return interval
        return None


    def get_interval_by_end_time(self, end):
        """
        Returns the interval with stop time equals to end

        """
        for interval in self.intervals:
            if interval.stop == end:
                return interval
        return None

    def get_intervals(self):
        """
        Returns all intervals associated with the resource request
        """
        return self.intervals