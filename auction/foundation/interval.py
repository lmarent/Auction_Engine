#interval.py
import datetime
from datetime import timedelta
from foundation.config import Config

class Interval():
    """
    This class represents a request interval for auctioning.
    """
    def __init__(self, start=None, stop=None, duration=0, interval=None, align=None):
        self.start = start
        self.stop = stop
        self.duration = duration 
        self.interval = interval
        self.align = align
        self.session = None

    def set_session(self, session):
        """
        Sets the session assigned to the intervals for auctioning
        """
        self.session = session

    @staticmethod
    def parse_time(start_at_least, stime):
        """
        Parse the start time field within the interval.
        :param start_at_least : datetime to start the interval
        :param stime time in time format to start the interval.
        Returns start datetime.
        """
        config = Config().get_config()
        time_format = config['Main']['TimeFormat']
        # parse time given
        if stime[0] == '+':
            seconds = int(stime[1:])
            time_val = datetime.datetime.now() + timedelta(seconds=seconds)
        else:
            time_val = datetime.strptime(stime, time_format)

        if time_val == 0:
            raise ValueError("Invalid time {}".format(stime))
        if time_val < start_at_least:
            raise ValueError("Invalid time {0}, it should be greater than \
                        previous interval stop {1}".format(stime, str(start_at_least)))
        return time_val

    @staticmethod
    def parse_interval_align(sinterval, salign):
        """
        Parse parameters interval and align within an interval.
        """
        inter = 0
        align = 0

        if sinterval:
            inter = int(sinterval)

        if salign:
            align = 1

        return inter, align

    def parse_interval(self, interval_dict, start_at_least):
        """
        Parsers an interval represented by the interval dictionary.

        :param interval_dict: interval dictionary representation
        :param start_at_least: datetime for the start of the interval.
        """
        # stop = 0 indicates infinite running time
        self.stop = 0

        #duration = 0 indicates no duration set
        self.duration = 0

        sstart = interval_dict.get('start',None)
        sstop = interval_dict.get('stop',None)
        sduration = interval_dict.get('duration',None)
        sinterval = interval_dict.get('interval', None)
        salign = interval_dict.get('align', None)

        if sstart and sstop and sduration:
            raise ValueError("illegal to specify: start+stop+duration time")
        
        if sstart:
            self.start = self.parse_time(start_at_least, sstart)
        else:
            self.start = start_at_least
        
        if sstop:
            self.stop = self.parse_time(start_at_least, sstop)

        self.duration = int(sduration)
        if self.duration > 0:
            if self.stop:
                self.start = self.stop - timedelta(seconds=self.duration)
            else:
                self.stop = self.start + timedelta(seconds=self.duration)

        if self.stop != 0 and self.stop < datetime.datetime.now():
            raise ValueError('resource request running time is already over')

        if self.start < datetime.datetime.now():
            self.start = datetime.datetime.now()

        self.interval, self.align = self.parse_interval_align(sinterval, salign)
