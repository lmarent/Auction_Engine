from foundation.session import Session
from datetime import datetime
from auction_client.resource_request_interval import ResourceRequestInterval
from auction_client.server_connection import ServerConnection


class AuctionSession(Session):
    """
    This class represents the agent client sessions used to auction. 

    It has the resource request interval, the auctions being performed,
    and the start and stop time when it should happen the auction session.
    """	

    def __init__(self, session_id: str, s_sender_address: str, s_destin_address:str,
                 sender_port: int, destin_port: int, protocol: int):

        super(AuctionSession,self).__init__(session_id, s_sender_address, sender_port,
                                            s_destin_address, destin_port, protocol)

        self.start_time = datetime.now()
        self.stop_time = datetime.now()
        self.resource_request_interval = None
        self.server_connection = None
        
        # Sets of auction identifiers. 
        self.auction_set = set()

    def set_start(self, start:datetime):
        """
        Sets the start time for the session
        :param start: start time
        """
        self.start_time = start

    def set_stop(self, stop: datetime):
        """
        Sets the stop time for the session
        :param stop: stop time
        """
        self.stop_time = stop

    def set_resource_request_interval(self, resource_request_interval: ResourceRequestInterval):
        """
        Sets the resource request interval for the session

        :param resource_request: resource request to set
        """
        self.resource_request_interval = resource_request_interval

    def get_auctions(self) -> set:
        """
        Returns the auction identifiers associated to the session.
        """
        return self.auction_set

    def set_auctions(self, auctions: list):
        """
        Copies the auctions identifiers within auctions parameter to the auction_set attribute.

        :param auctions - auctions' identifiers to be copied. 
        """
        for auction_key in auctions:
            self.auction_set.add(auction_key)

    def set_server_connection(self, server_connection : ServerConnection):
        """
        Sets the server connection established for the session.
        """
        self.server_connection = server_connection
        server_connection.add_reference()

    def get_server_connnection(self) -> ServerConnection:
        """
        Gets the server connection established for the session.
        :return: server connection
        """
        return self.server_connection

    def get_resource_request_interval(self):
        """
        Gets the resource request interval for the session

        :return:
        """
        return self.resource_request_interval