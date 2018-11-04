#resource_request.py
import datetime
from  foundation.auctioning_object import AuctioningObject
from .interval import Interval

class ResourceRequest(AuctioningObject):
    """
    This class repreesents resouce request from users to be purchsed in the market.
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
    def parse_time(startatleast, stime):
        """
        Parse the start time field within the interval. 
        Returns start datetime.
        """

        # parse tiem given 
        if stime[0] == '+':
            seconds = int(stime[1:])
            time_val = datetime.datetime.now() + seconds
        else:
            time_val = datetime.strptime(stime, self.timeformat)

        if time_val == 0:
            raise ValueError("Invalid time {}".format(sstart)) 
        if time_val < startatleast:
            raise ValueError("Invalid time {0}, it should be greater than \
                        previous interval stop {1}".format(stime, str(startatleast)))
        return time_val

    @staticmethod
    def parse_interval_align(sinterval, salign):
        """
        Parse parameters interval and align within an interval.
        """
        inter = 0
        inter = int(sinterval)
        if salign:
            align = 1
        else:
            align = 0

        return inter, align


    @staticmethod
    def parse_interval(interval, startatleast):
        # stop = 0 indicates infinite running time
        stop = 0

        #duration = 0 indicates no duration set
        duration = 0

        start = startatleast
        sstart = interval.getElementsByTagName('Start')[0]
        sstop = interval.getElementsByTagName('Stop')[0]
        sdurantion = interval.getElementsByTagName('Duration')[0]
        sinterval = interval.getElementsByTagName('Interval')[0]
        salign = interval.getElementsByTagName('Align')[0]

        if sstart and sstop and sdurantion:
            raise ValueError("illegal to specify: start+stop+duration time")
        
        if sstart:
            start = self.parse_time(startatleast, sstart)
        
        if sstop:
            stop = self.parse_time(startatleast, sstop)
        
        duration = int(sduration)
        if duration > 0:
            if stop:
                start = stop - duration
            else:
                stop = start + duration

        if stop != 0 and stop < now
            raise ValueError('resource request running time is already over')

        if start < now:
            start = now

        interval, align = self.parse_interval_align(sinterval, salign)
        new_interval = Interval( start, stop, duration, interval, align ) 
        return start, new_interval


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