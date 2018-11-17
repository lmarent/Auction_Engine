#interval.py
import datetime 

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
            raise ValueError("Invalid time {}".format(stime))
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

    def parse_interval(self, interval_dict, startatleast):
        # stop = 0 indicates infinite running time
        self.stop = 0

        #duration = 0 indicates no duration set
        self.duration = 0

        start = startatleast
        sstart = interval_dict['Start']
        sstop = interval_dict['Stop']
        sduration = interval_dict['Duration']
        sinterval = interval_dict['Interval']
        salign = interval_dict['Align']

        if sstart and sstop and sduration:
            raise ValueError("illegal to specify: start+stop+duration time")
        
        if sstart:
            self.start = self.parse_time(startatleast, sstart)
        
        if sstop:
            self.stop = self.parse_time(startatleast, sstop)
        
        self.duration = int(sduration)
        if self.duration > 0:
            if self.stop:
                self.start = self.stop - self.duration
            else:
                self.stop = self.start + self.duration

        if self.stop != 0 and self.stop < datetime.datetime.now()
            raise ValueError('resource request running time is already over')

        if self.start < datetime.datetime.now():
            self.start = datetime.datetime.now()

        self.interval, self.align = self.parse_interval_align(sinterval, salign)
