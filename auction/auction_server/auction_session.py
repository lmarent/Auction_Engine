from foundation.session import Session
from auction_server.server_message_processor import ClientConnection

class AuctionSession(Session):
    """
    This class represents the server sessions used to auction.
    """

    def __init__(self, session_id: str, s_sender_address: str, s_destin_address: str,
                 sender_port: int, destin_port: int, protocol: int):
        super(AuctionSession, self).__init__(session_id, s_sender_address, sender_port,
                                             s_destin_address, destin_port, protocol)

        self.connection = None

    def set_connection(self, client_connection: ClientConnection):
        """
        Sets the client connection established for the session.
        """
        self.connection = client_connection

    def get_connnection(self) -> ClientConnection:
        """
        Gets the client connection established for the session.
        :return: client connection
        """
        return self.connection
