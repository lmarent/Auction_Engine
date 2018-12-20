

class AuctionSession(Session):
    """
    This class represents the agent client sessions used to auction. 
    It has the resource request, the auctions being performed, 
    and the start and stop time within it should happen the auction session.
    """	

    def __init__(self, start_time, stop_time, resource_request):
        self.start_time = starttime
        self.stop_time = stoptime
        self.resource_request = resource_request
        
        # Sets of auction identifiers. 
        self.auction_set = Set()

    def get_auctions():
        """
        Returns the auction identifiers associated to the session.
        """
        return self.auction_set

    def set_auction(auctions: Set):
        """
        Copies the auctions identifiers within auctions parameter to the auction_set attribute.

        :param auctions - auctions' identifiers to be copied. 
        """
        for identifier in auctions:
            self.auction_set.add(identifier)
