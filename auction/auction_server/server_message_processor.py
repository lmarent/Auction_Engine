from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType
import uuid

from enum import Enum

from auction_server.server_main_data import ServerMainData
from auction_server.auction_server_handler import HandleAuctionMessage

from foundation.auction_message_processor import AuctionMessageProcessor
from foundation.session import Session

from python_wrapper.ipap_message import IpapMessage
from utils.auction_utils import log


class ClientConnectionState(Enum):
    """
    States for a client connection.
    """
    LISTEN = 0
    SYN_RCVD = 1
    ESTABLISHED = 2
    FIN_WAIT_1 = 3
    FIN_WAIT_2 = 4
    TIME_WAIT = 5
    CLOSE_WAIT = 6
    LAST_ACK = 7
    CLOSE = 8


class ClientConnection:
    def __init__(self, key: str):
        self.key = key
        self.state = ClientConnectionState.LISTEN
        self.session = None
        self.web_socket = None
        self.references = 0

    def set_web_socket(self, ws: WebSocketResponse):
        """
        Sets the web socket created for the connection
        :param ws: web socket used
        :return:
        """
        self.web_socket = ws

    def set_session(self, session: Session):
        """
        Sets the session created for the connection
        :param session: session used
        :return:
        """
        self.session = session

    def set_state(self, state: ClientConnectionState):
        """
        Sets the state of the client connection.

        :param state: new state to set
        """
        self.state = state

    def get_state(self) -> ClientConnectionState:
        """
        Gets the current state of the connection.
        :return: connection's state
        """
        return self.state


class ServerMessageProcessor(AuctionMessageProcessor):
    """
    This class takes care of agents' communications.
    """

    def __init__(self):
        self.server_data = ServerMainData()
        super(ServerMessageProcessor, self).__init__(self.server_data.domain)
        self.logger = log().get_logger()

    async def handle_syn(self, session: Session,
                         client_connection: ClientConnection,
                         ipap_message: IpapMessage):
        """
        Handles the arrival of a syn message.

        :param session:session: object that waas created to manage this connection
        :param client_connection: client connection object created for manage the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        # verifies the connection state
        if client_connection.state == ClientConnectionState.LISTEN:
            # send the ack message establishing the session.
            message = self.build_syn_ack_message(session.get_next_message_id(), ipap_message.get_seqno())
            self.send_message(client_connection, message.get_message())

        else:
            # The server is not in syn sent state, so ignore the message
            self.logger.info("a message with syn was received, but the session \
                                is not in LISTEN. Ignoring the message")

    async def handle_ack(self, session: Session,
                         client_connection: ClientConnection,
                         ipap_message: IpapMessage):
        """
        Handles the arrival of a ack message.

        :param session:session: object that waas created to manage this connection
        :param client_connection: client connection object created for manage the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        # verifies the connection state
        if client_connection.state == ClientConnectionState.SYN_RCVD:
            try:
                session.confirm_message(ack_seqno)
                client_connection.set_state(ClientConnectionState.ESTABLISHED)

            except ValueError as e:
                self.logger.info("The message ack is not the expected, so ignore the message")
                # The message ack is not the expected, so ignore the message
                pass

        elif client_connection.state == ClientConnectionState.LAST_ACK:
            try:
                session.confirm_message(ack_seqno)
                client_connection.set_state(ClientConnectionState.CLOSE)

            except ValueError as e:
                self.logger.info("The message ack is not the expected, so ignore the message")
                pass
        else:
            when = 0
            handle_auction_message = HandleAuctionMessage(session, ipap_message, when)
            handle_auction_message.start()

    async def handle_fin(self, session: Session,
                         client_connection: ClientConnection,
                         ipap_message: IpapMessage):
        """
        Handles the arrival of a ack message.

        :param session:session: object that waas created to manage this connection
        :param client_connection: client connection object created for manage the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        # verifies the connection state
        if client_connection.state == ClientConnectionState.ESTABLISHED:
            try:
                session.confirm_message(ack_seqno)
                message = self.build_ack_message(session.get_next_message_id(), ipap_message.get_seqno())
                self.send_message(client_connection, message.get_message())
                client_connection.set_state(ClientConnectionState.CLOSE_WAIT)

                # TODO: CALL THE APP TO SHUTDOWN

                message = self.build_fin_message(session.get_next_message_id(), 0)
                self.send_message(client_connection, message.get_message())
                client_connection.set_state(ClientConnectionState.LAST_ACK)

            except ValueError as e:
                # The message ack is not the expected, so ignore the message
                pass
        else:
            # The server is not in established state, so ignore the message
            self.logger.info("A msg with fin state was received,but the server \
                                is not in established state, ignoring it")

    async def process_message(self, client_connection: ClientConnection, msg: str):
        """
        Process a message arriving from an agent.

        :param server_connection: websocket and aiohttp session created for the connection
        :param msg: message
        :return:
        """
        ipap_message = self.is_auction_message(msg)
        if ipap_message is not None:
            syn = ipap_message.get_syn()
            ack = ipap_message.get_ack()
            fin = ipap_message.get_fin()
            session = self.auction_session_manager.get(client_connection.key)

            if syn:
                self.handle_syn(session, client_connection, ipap_message)

            elif ack:
                self.handle_ack(session, client_connection, ipap_message)

            elif fin:
                self.handle_fin(session, client_connection, ipap_message)

            else:
                # Normal bidding message.
                pass
        else:
            # invalid message, we do not send anything for the moment
            self.logger.error("Invalid message from agent with domain {}")
            pass

    async def handle_web_socket(self, request):
        """
        Handles a new arriving web socket

        :param request: request received.
        :return:
        """
        ws = WebSocketResponse()
        await ws.prepare(request)

        session_id = str(uuid.uuid1())
        ip_address = self.server_data.ip_address4
        if self.server_data.use_ipv6:
            ip_address = self.server_data.ip_address6

        peername = request.transport.get_extra_info('peername')
        host, port = peername

        session = Session(session_id, ip_address, self.server_data.local_port,
                          host, port, self.server_data.protocol)

        client_connection = ClientConnection(session_id)

        # Put in the list the new connection from the client.
        request.app['web_sockets'].append(ws)
        try:
            async for msg in ws:
                if msg.type == WSMsgType.text:
                    await self.process_message(ws, msg)

                elif msg.type == WSMsgType.error:
                    self.logger.debug('ws connection closed with exception %s' % ws.exception())

                elif msg.type == WSMsgType.close:
                    self.logger.debug('ws connection closed')
        finally:
            request.app['web_sockets'].remove(ws)

        self.logger.debug('websocket connection closed')
        return ws

    async def send_message(self, client_connection: ClientConnection, message: str):
        """
        Sends the message for an agent

        :param message: message to be send
        """
        client_connection.web_socket.send_str(message)
