from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType
from aiohttp import WSCloseCode
import uuid

from enum import Enum

from auction_server.server_main_data import ServerMainData
from foundation.session import Session

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
    CLOSED = 8


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

    def get_auction_session(self) -> Session:
        """
        Gets the auction session
        :return:
        """
        return self.session

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

    def get_reference(self):
        """
        Returns the number of references.
        :return:
        """
        return self.references


class ServerMessageProcessor(AuctionMessageProcessor, metaclass=Singleton):
    """
    This class takes care of agents' communications.
    """
    from auction_server.auction_session import AuctionSession

    def __init__(self):
        self.server_data = ServerMainData()
        super(ServerMessageProcessor, self).__init__(self.server_data.domain)
        self.session_manager = SessionManager()
        self.logger = log().get_logger()

    async def websocket_shutdown(self, client_connection: ClientConnection):
        """
        Disconnects the websocket from the server

        :param client_connection: client to disconnect
        :return:
        """
        self.logger.info('starting websocket shutdown - key {0}'.format(client_connection.key))

        # Close open sockets
        if not client_connection.web_socket.closed:
            await client_connection.web_socket.close(code=WSCloseCode.GOING_AWAY, message='Client shutdown')

        self.logger.info('websocket shutdown ended - key {0}'.format(client_connection.key))

    async def _disconnect_socket(self, client_connection: ClientConnection):
        """
        disconnects a session from the server.

        :param client_connection:  connection being used.
        :return:
        """
        self.logger.debug("Starting _disconnect_socket - nbr references:{0}".format(
            str(client_connection.get_reference())))

        client_connection.delete_reference()
        if client_connection.get_reference() <= 0:
            # the shutdown of the websocket also finishes the task.
            await self.websocket_shutdown(client_connection)
            self.logger.debug("sent socket shutdown to the server")

        self.logger.debug("Ending _disconnect_socket")

    async def handle_syn(self, session: AuctionSession, ipap_message: IpapMessage):
        """
        Handles the arrival of a syn message.

        :param session: session that is handling the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        self.logger.debug("starting handle_syn")
        # verifies the connection state
        if session.get_connection().state == ClientConnectionState.LISTEN:
            # send the ack message establishing the session.

            message = self.build_syn_ack_message(session.get_next_message_id(),
                                                 ipap_message.get_seqno())

            session.add_pending_message(message)
            await self.send_message(session.get_connection(), message.get_message())

            session.get_connection().set_state(ClientConnectionState.SYN_RCVD)

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
        if session.get_connection().state == ClientConnectionState.SYN_RCVD:
            try:
                session.confirm_message(ack_seqno)
                session.get_connection().set_state(ClientConnectionState.ESTABLISHED)

                self.logger.info('New established connection')

            except ValueError:
                self.logger.info("The message ack is not the expected, so ignore the message")

        # verifies the connection state is in fin wait 1
        elif session.get_connection().state == ClientConnectionState.FIN_WAIT_1:
            try:
                session.confirm_message(ack_seqno)
                session.get_connection().set_state(ClientConnectionState.FIN_WAIT_2)

            except ValueError:
                self.logger.info("A msg with ack nbr not expected was received, ignoring it")

        elif session.get_connection().state == ClientConnectionState.LAST_ACK:
            try:
                session.confirm_message(ack_seqno)
                session.get_connection().set_state(ClientConnectionState.CLOSE)

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
        if session.get_connection().state == ClientConnectionState.ESTABLISHED:
            message = self.build_ack_message(session.get_next_message_id(),
                                             ipap_message.get_seqno())

            await self.send_message(session.get_connection(), message.get_message())
            session.get_connection().set_state(ClientConnectionState.CLOSE_WAIT)

            from auction_server.auction_server_handler import HandleClientTearDown
            handle_tear_down = HandleClientTearDown(session)
            await handle_tear_down.start()

            message = self.build_fin_message(session.get_next_message_id(), 0)
            session.add_pending_message(message)
            await self.send_message(session.get_connection(), message.get_message())
            session.get_connection().set_state(ClientConnectionState.LAST_ACK)

        elif session.get_connection().state == ClientConnectionState.FIN_WAIT_2:

            self.logger.debug("receive the fin message when in fin_wait")
            # send the ack message establishing the session.
            message = self.build_ack_message(session.get_next_message_id(), ipap_message.get_seqno())

            await self.send_message(session.get_connection(), message.get_message())

            session.get_connection().set_state(ClientConnectionState.CLOSED)
            await self._disconnect_socket(session.get_connection())
            self.session_manager.del_session(session.get_key())

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

        from auction_server.auction_session import AuctionSession
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
            if session_id in self.session_manager.get_session_keys():
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
