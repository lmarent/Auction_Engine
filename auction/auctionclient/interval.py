#interval.py

class Interval():
    """
    This class represents a request interval for auctioning.
    """
	def __init__(self, start,  stop,  duration, interval, align):
        self.start = start
        self.stop = stop
        self.duration = duration 
        self.interval = interval
        self.align = align
        self.session = None

    def set_session(session):
        """
        Sets the session assigned to the intervals for auctioning
        """
        self.session = session