#bidding_object.py
from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType

from datetime import datetime


class BiddingObject(AuctioningObject):
    """
    This class respresents the bidding objects being interchanged between users and the auctionner. 
    A bidding object has two parts:
    
      1. A set of elements which establish a route description
      2. A set of options which establish the duration of the bidding object. 
    """

    def __init__(self, auction_key: str, bidding_object_key:str, object_type: AuctioningObjectType,
                    elements:dict, options: dict):

        assert( object_type==AuctioningObjectType.BID or object_type==AuctioningObjectType.ALLOCATION )
        super(BiddingObject, self).__init__(bidding_object_key, object_type)

        self.elements = elements
        self.options = options
        self.parent_auction = auction_key

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
        if option_name in self.optios.keys():
            return self.options[option_name]
        else:
            raise ValueError('Option with name: {} was not found'.format(option_name))

    def calculate_intervals(self):

        laststart = datetime.now()
        laststop = datetime.now()
        duration = 0

        optionListIter_t iter;
        for option_id in self.options:

            duration = 0;
            biddingObjectInterval_t
            biddingObjectInterval;
            biddingObjectInterval.start = 0;
            biddingObjectInterval.stop = 0;

            field_t fstart = getOptionVal(iter->first, "Start");
            field_t fstop = getOptionVal(iter->first, "Stop");
            field_t fduration = getOptionVal(iter->first, "BiddingDuration");

            # ifdef DEBUG
                log->dlog(ch, "BiddingObject: %s.%s - fstart %s", getSet().c_str(),
                          getName().c_str(), (fstart.getInfo()).c_str());

                log->dlog(ch, "BiddingObject: %s.%s - fstop %s", getSet().c_str(),
                          getName().c_str(), (fstop.getInfo()).c_str());

                log->dlog(ch, "BiddingObject: %s.%s - fduration %s", getSet().c_str(),
                          getName().c_str(), (fduration.getInfo()).c_str());
            # endif

            if ((fstart.mtype == FT_WILD) & &
                    (fstop.mtype == FT_WILD) & &
                    (fduration.mtype == FT_WILD))
            {
                throw Error(409, "illegal to specify: start+stop+duration time");
            }

            if (fstart.mtype != FT_WILD) {
                string sstart = ((fstart.value)[0]).getString();
                biddingObjectInterval.start = ParserFcts::parseTime(sstart);
                if (biddingObjectInterval.start == 0) {
                    throw Error(410, "invalid start time %s", sstart.c_str());
                }
            }

            if (fstop.mtype != FT_WILD) {
                string sstop = ((fstop.value)[0]).getString();
                biddingObjectInterval.stop = ParserFcts::parseTime(sstop);
                if (biddingObjectInterval.stop == 0) {
                    throw Error(411, "invalid stop time %s", sstop.c_str());
                }
            }

            if (fduration.mtype != FT_WILD) {
                string sduration = ((fduration.value)[0]).getString();
                duration = ParserFcts::parseULong(sduration);
            }

            if (duration > 0) {
                if (biddingObjectInterval.stop) {
                    # stop + duration specified
                    biddingObjectInterval.start = biddingObjectInterval.stop - duration;
                } else {
                    #stop[+ start] specified
        
                    if (biddingObjectInterval.start) {
                        biddingObjectInterval.stop = biddingObjectInterval.start + duration;
                    } else {
                        biddingObjectInterval.start = laststop;
                        biddingObjectInterval.stop = biddingObjectInterval.start + duration;
                    }
                }
            }

            # ifdef DEBUG
            log->dlog(ch, "BiddingObject: %s.%s - now:%s stop %s", getSet().c_str(),
            getName().c_str(), Timeval::
                toString(now).c_str(),
                Timeval::toString(biddingObjectInterval.stop).c_str());
            # endif

            # now start has a defined value, while stop may still be zero
            # indicating an infinite rule

            # do we have a stop time defined that is in the past ?
            if ((biddingObjectInterval.stop != 0) & & (biddingObjectInterval.stop <= now)) {
                log->dlog(ch, "Bidding object running time is already over");
            }

            if (biddingObjectInterval.start < now) {
                # start late tasks immediately
                biddingObjectInterval.start = now;
            }

            laststart = biddingObjectInterval.start;
            laststop = biddingObjectInterval.stop;

            list->push_back(pair < time_t, biddingObjectInterval_t > (biddingObjectInterval.start, biddingObjectInterval));

        }