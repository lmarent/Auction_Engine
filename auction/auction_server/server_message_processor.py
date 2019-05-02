from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType
import uuid

from enum import Enum

from auction_server.server_main_data import ServerMainData
from auction_server.auction_session import AuctionSession

from foundation.auction_message_processor import AuctionMessageProcessor
from foundation.session_manager import SessionManager

from python_wrapper.ipap_message import IpapMessage
from utils.auction_utils import log
from foundation.singleton import Singleton


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

    def set_session(self, session: AuctionSession):
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

    def get_auction_session(self) -> AuctionSession:
        """
        Gets the auction session
        :return:
        """
        return self.session


class ServerMessageProcessor(AuctionMessageProcessor, metaclass=Singleton):
    """
    This class takes care of agents' communications.
    """

    def __init__(self):
        self.server_data = ServerMainData()
        super(ServerMessageProcessor, self).__init__(self.server_data.domain)
        self.session_manager = SessionManager()
        self.logger = log().get_logger()

    async def handle_syn(self, session: AuctionSession, ipap_message: IpapMessage):
        """
        Handles the arrival of a syn message.

        :param session: session that is handling the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        self.logger.debug("starting handle_syn")
        # verifies the connection state
        if session.get_connnection().state == ClientConnectionState.LISTEN:
            # send the ack message establishing the session.

            message = self.build_syn_ack_message(session.get_next_message_id(),
                                                 ipap_message.get_seqno())

            session.add_pending_message(message)
            await self.send_message(session.get_connnection(), message.get_message())

            session.get_connnection().set_state(ClientConnectionState.SYN_RCVD)

        else:
            # The server is not in syn sent state, so ignore the message
            self.logger.info("a message with syn was received, but the session \
                                is not in LISTEN. Ignoring the message")

        self.logger.debug("Ending handle_syn")

    async def handle_ack(self, session: AuctionSession, ipap_message: IpapMessage):
        """
        Handles the arrival of a ack message.

        :param session: session that is handling the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        self.logger.debug('starting handle_ack')
        from auction_server.auction_server_handler import HandleAuctionMessage

        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        # verifies the connection state
        if session.get_connnection().state == ClientConnectionState.SYN_RCVD:
            try:
                session.confirm_message(ack_seqno)
                session.get_connnection().set_state(ClientConnectionState.ESTABLISHED)

                self.logger.info('New established connection')

            except ValueError:
                self.logger.info("The message ack is not the expected, so ignore the message")

        elif session.get_connnection().state == ClientConnectionState.LAST_ACK:
            try:
                session.confirm_message(ack_seqno)
                session.get_connnection().set_state(ClientConnectionState.CLOSE)

                self.logger.info("The connection has been closed")
            except ValueError:
                self.logger.info("The message ack is not the expected, so ignore the message")

        else:
            when = 0
            handle_auction_message = HandleAuctionMessage(session, ipap_message, when)
            handle_auction_message.start()

        self.logger.debug('Ending handle_ack')

    async def handle_fin(self, session: AuctionSession,
                         ipap_message: IpapMessage):
        """
        Handles the arrival of a fin message.

        :param session: session that is handling the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        self.logger.debug("Starting  handle_fin")
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        try:
            session.confirm_message(ack_seqno)
        except ValueError:
            # The message ack is not the expected, so just ignore it
            pass

        # verifies the connection state
        if session.get_connnection().state == ClientConnectionState.ESTABLISHED:
            message = self.build_ack_message(session.get_next_message_id(),
                                             ipap_message.get_seqno())

            await self.send_message(session.get_connnection(), message.get_message())
            session.get_connnection().set_state(ClientConnectionState.CLOSE_WAIT)

            from auction_server.auction_server_handler import HandleClientTearDown
            handle_tear_down = HandleClientTearDown(session)
            await handle_tear_down.start()

            message = self.build_fin_message(session.get_next_message_id(), 0)
            session.add_pending_message(message)
            await self.send_message(session.get_connnection(), message.get_message())
            session.get_connnection().set_state(ClientConnectionState.LAST_ACK)

        else:
            # The server is not in established state, so ignore the message
            self.logger.info("A msg with fin state was received,but the server \
                                is not in established state, ignoring it")

        self.logger.debug("Ending handle_fin")

    async def process_message(self, session: AuctionSession, msg: str):
        """
        Process a message arriving from an agent.

        :param session: session that is handling the connection
        :param msg: message
        :return:
        """
        try:

            ipap_message = self.is_auction_message(msg)

        except ValueError as e:
            # invalid message, we do not send anything for the moment
            self.logger.error("Invalid message from agent - Received msg: {0} - Error {1}".format(msg, str(e)))
            return

        syn = ipap_message.get_syn()
        ack = ipap_message.get_ack()
        fin = ipap_message.get_fin()
        if syn:
            await self.handle_syn(session, ipap_message)

        elif ack:
            await self.handle_ack(session, ipap_message)

        elif fin:
            await self.handle_fin(session, ipap_message)

        else:
            from auction_server.auction_server_handler import HandleAuctionMessage
            handle_auction_message = HandleAuctionMessage(session, ipap_message, 0)
            handle_auction_message.start()
            pass

    async def handle_web_socket(self, request):
        """
        Handles a new arriving web socket

        :param request: request received.
        :return:
        """
        self.logger.debug('starting handle_web_socket')
        ws = WebSocketResponse()
        await ws.prepare(request)

        session_id = str(uuid.uuid1())
        ip_address = self.server_data.ip_address4
        if self.server_data.use_ipv6:
            ip_address = self.server_data.ip_address6

        peername = request.transport.get_extra_info('peername')
        host, port = peername

        session = AuctionSession(session_id, ip_address, self.server_data.local_port,
                                 host, port, self.server_data.protocol)

        client_connection = ClientConnection(session_id)
        client_connection.set_web_socket(ws)
        client_connection.set_session(session)
        session.set_connection(client_connection)
        self.session_manager.add_session(session)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.text:
                    await self.process_message(session, msg.data)

                elif msg.type == WSMsgType.error:
                    self.logger.debug('ws connection closed with exception %s' % ws.exception())

                elif msg.type == WSMsgType.close:
                    self.logger.debug('ws connection closed')
        finally:
            self.session_manager.del_session(session_id)
            self.logger.debug('# active sessions: {0}'.format(str(len(self.session_manager.session_objects))))

        self.logger.debug('websocket connection closed')
        return ws

    async def process_disconnect(self, session: AuctionSession):
        """
        Teardowns the connection established for a particular session.

        :param session: session to teardown
        :return:
        """
        self.logger.debug('Starting to disconnect')

        # verifies the connection state
        if session.connection.state == ClientConnectionState.ESTABLISHED:

            # send the ack message establishing the session.
            message = self.build_fin_message(session.get_next_message_id(), 0)

            session.add_pending_message(message)
            await self.send_message(session.connection, message.get_message())

            session.connection.set_state(ClientConnectionState.FIN_WAIT_1)

        else:
            # The connection is not in establised state, so generate an error
            raise ValueError("Error the connection for session key {0} is not established".format(session.get_key()))

        self.logger.debug('Ending disconnect')

    async def send_message(self, client_connection: ClientConnection, message: str):
        """
        Sends the message for an agent

        :param client_connection: websocket and aiohttp session created for the connection
        :param message: message to be send
        """
        self.logger.debug('Start send message')
        await client_connection.web_socket.send_str(message)
        self.logger.debug('End send message')
