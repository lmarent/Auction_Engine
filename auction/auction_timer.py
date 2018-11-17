from foundation.singleton import Singleton

class TickDuration:
    """
    This class stores a line of measured clock ticks

    Attributes:
    ----------
    start:  start clock tick counter
    last:   clock tick duration for last measurement
    sum:    accumulated clock ticks
    num:    number of measurements
    """
    def __init__(self, start, last, sum, num):
        self.start = start
        self.last = last
        self.sum = sum
        self.num = num


class AuctionTime(metaclass=Singleton):
    """
    This class stores timestamps for auction processes

    Attributes
    ----------

    clock_speed:    system clock speed in MHz
    overhead:       wasted CPU cycles per measurement
    ticks           list of performance measurement results
    """

    def __init__(self):
        """
        constructs and initializes a AuctionTimer object
        """

    def _read_clock_speed(self) -> float:
        """
        reads system clock speed from /proc/cpuinfo
        :return: system clock speed in MHz, -1.0 if not available
        """

    def read_time_speed_clock(self):
        """
        reads system clock tick counter from cpu
        :return: number of CPU clock ticks since last reboot
        """


    def get_clock_speed(self):
        """
        gets system clock speed in MHz
        :return: system clock speed in MHz, -1.0 if not available
        """

    def start(self, slot):
        """
        starts measurement for one slot
        :param slot: number of measurement slot
        """

    def stop(self, slot):
        """
        ends measurement for one slot and record number of ticks
        :param slot: number of measurement slot
        """

    def account(self, slot, ticks):
        """
        account measurement with 'ticks' clock ticks for slot 'slot'
        :param  slot:   number of measurement slot
        :param  ticks:  number of CPU clock ticks from independant measurement
        :return:
        """

    def latest(self, slot):
        """
        calculates number of nsec taken for latest measurements for one specific slot
        :param slot : number of measurement slot
        :return: returns the number of nsec taken for latest measurements for one specific slot
        """

    def avg(self, slot : int):
        """
        calculate average number of nsec taken for measurements for one slot

        :param slot: number of measurement slot
        :return: the average number of nsec taken for measurements for one slot
        """

    @staticmethod
    def ticks_2_ns(runs :int, ticks ):
        """
        Converts number of clock ticks into number of nanoseconds
        :param runs     number of measurements that accumulated the clock tick
        :param ticks    number of accumulated clock ticks
        :return:   number of nanoseconds elapsed during one measurement on average
        """

    @staticmethod
    def ticks_2_ns():