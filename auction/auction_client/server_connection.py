from aiohttp import ClientSession
from aiohttp.client_ws import ClientWebSocketResponse
from enum import Enum
from foundation.session import Session


class ServerConnectionState(Enum):
    """
    States for a server connection.
    """
    CLOSED = 0
    SYN_SENT = 1
    ESTABLISHED = 2
    FIN_WAIT_1 = 3
    FIN_WAIT_2 = 4
    TIME_WAIT = 5


class ServerConnection:
    def __init__(self, key: str):
        self.key = key
        self.state = ServerConnectionState.CLOSED
        self.task = None
        self.auction_session = None
        self.session = None
        self.web_socket = None
        self.references = 0

    def set_web_socket(self, session: ClientSession, ws: ClientWebSocketResponse):
        """
        Sets the session and web socket created for the connection
        :param session: client session used
        :param ws: web socket used
        :return:
        """
        self.session = session
        self.web_socket = ws

    def set_task(self, task):
        """
        Sets the task created to listen in the web socket
        :param task: web socket task
        :return:
        """
        self.task = task

    def add_reference(self):
        """
        increases the number of objects referencing this connection
        """
        self.references = self.references + 1

    def delete_reference(self):
        """
        increases the number of objects referencing this connection
        """
        self.references = self.references - 1

    def set_state(self, state: ServerConnectionState):
        """
        Sets the state of the server connection.

        :param state: new state to set
        """
        self.state = state

    def get_state(self) -> ServerConnectionState:
        """
        Gets the current state of the connection.
        :return: connection's state
        """
        return self.state

    def set_auction_session(self, session: Session):
        """
        Sets the auction session for which we create the server connection.

        :param session: session to set
        """
        self.auction_session = session

    def get_auction_session(self,) -> Session:
        """
        Gets the auction session for which we create the server connection.

        :param session: session to set
        """
        return self.auction_session