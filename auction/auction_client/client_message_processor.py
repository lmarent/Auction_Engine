import asyncio
from aiohttp import ClientSession
from aiohttp import WSMsgType
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp import WSCloseCode

from ipaddress import ip_address
import os
import signal

from foundation.auction_message_processor import AuctionMessageProcessor

from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.client_main_data import ClientMainData
from auction_client.auction_session import AuctionSession
from auction_client.server_connection import ServerConnectionState
from auction_client.server_connection import ServerConnection
from python_wrapper.ipap_message import IpapMessage

from utils.auction_utils import log
from foundation.singleton import Singleton


class ClientMessageProcessor(AuctionMessageProcessor, metaclass=Singleton):
    """
    This class takes care of agents' communications.
    """

    def __init__(self, app=None):

        self.client_data = ClientMainData()
        super(ClientMessageProcessor, self).__init__(self.client_data.domain)
        self.app = app
        self.auction_session_manager = AuctionSessionManager()
        self.logger = log().get_logger()

    async def websocket_shutdown(self, server_connection: ServerConnection):
        """
        Disconnects the websocket from the server

        :param server_connection: server to disconnect
        :return:
        """
        self.logger.info('starting server connection shutdown - key {0}'.format(server_connection.key))

        # Close open sockets
        if server_connection.session:
            session = server_connection.session
            if not session.closed:
                ws = server_connection.web_socket
                if not ws.closed:
                    await ws.close(code=WSCloseCode.GOING_AWAY,
                                   message='Client shutdown')
                await session.close()

        self.logger.info('server connection shutdown ended - key {0}'.format(server_connection.key))

    async def _connection_established(self, session):
        """
        Sleeps until the session is acknowledged or a timeout is reached.

        :param session: session to be acknowledged
        :raises Connection error when not acknowledged
        """
        timeout = self.TIMEOUT_SYN
        while timeout > 0:
            if session.server_connection.get_state() == ServerConnectionState.ESTABLISHED:
                break
            await asyncio.sleep(0.01)
            timeout = timeout - 10

        if timeout <= 0:
            # teardown the web socket connection
            await self.websocket_shutdown(session.server_connection)

            # Raise an exception to inform the error when connecting to the server.
            raise ConnectionError("The connection could not be established")

    async def connect(self) -> AuctionSession:
        """
        Connects a server, occurs per every resource request interval activation.
        """
        self.logger.debug('in client message processor connect')
        if self.client_data.use_ipv6:
            session = self.auction_session_manager.create_agent_session(self.client_data.ip_address6,
                                                                        self.client_data.destination_address6,
                                                                        self.client_data.source_port,
                                                                        self.client_data.destination_port,
                                                                        self.client_data.protocol)
        else:
            session = self.auction_session_manager.create_agent_session(self.client_data.ip_address4,
                                                                        self.client_data.destination_address4,
                                                                        self.client_data.source_port,
                                                                        self.client_data.destination_port,
                                                                        self.client_data.protocol)

        server_connection = ServerConnection(session.get_key())
        try:
            await self.websocket_connect(self.client_data.use_ipv6,
                                         self.client_data.destination_address4,
                                         self.client_data.destination_address6,
                                         self.client_data.destination_port,
                                         server_connection)

            server_connection.set_auction_session(session)
            task = asyncio.ensure_future(self.websocket_read(server_connection))
            server_connection.set_task(task)

        except ClientConnectorError as e:
            self.logger.error('error connecting the server {0}'.format(str(e)))
            raise e

        # we need to wait until the connection is ready
        message = self.build_syn_message(session.get_next_message_id())
        str_msg = message.get_message()
        await self.send_message(server_connection, str_msg)
        server_connection.set_state(ServerConnectionState.SYN_SENT)
        session.add_pending_message(message)
        session.set_server_connection(server_connection)

        await self._connection_established(session)

        return session

    async def _disconnect_socket(self, server_connection: ServerConnection):
        """
        disconnects a session from the server.

        :param server_connection: server connection being used.
        :return:
        """
        self.logger.debug("Starting _disconnect_socket - nbr references:{0}".format(
            str(server_connection.get_reference())))

        server_connection.delete_reference()
        if server_connection.get_reference() <= 0:
            # the shutdown of the websocket also finishes the task.
            await self.websocket_shutdown(server_connection)
            self.logger.debug("sent socket shutdown to the server")

        self.logger.debug("Ending _disconnect_socket")

    async def handle_syn_ack_message(self, server_connection: ServerConnection,
                                     ipap_message: IpapMessage):
        """
        Establishes the session
        :param server_connection: websocket and aiohttp session created for the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        self.logger.debug("Starting handle_syn_ack_message")
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        self.logger.debug("ack_seqno:{0}".format(str(ack_seqno)))

        # verifies the connection state
        if server_connection.state == ServerConnectionState.SYN_SENT:
            try:
                server_connection.get_auction_session().confirm_message(ack_seqno)

                # send the ack message establishing the session.
                syn_ack_message = self.build_ack_message(server_connection.get_auction_session().get_next_message_id(),
                                                         ipap_message.get_seqno())
                msg = syn_ack_message.get_message()
                await self.send_message(server_connection, msg)

                # puts the connection as established.
                server_connection.set_state(ServerConnectionState.ESTABLISHED)

                self.logger.info("Connection established with server")

            except ValueError:
                self.logger.error("Invalid ack nbr from the server, the session is going to be teardown")
                await self._disconnect_socket(server_connection)
                self.auction_session_manager.del_session(server_connection.get_auction_session().get_key())

        else:
            # The server is not in syn sent state, so ignore the message
            self.logger.info("a message with syn and ack was received, but the session \
                                is not in SYN_SENT. Ignoring the message")

        self.logger.debug("Ending handle_syn_ack_message")

    async def send_ack_disconnect(self, server_connection: ServerConnection,
                                  ipap_message: IpapMessage):
        """
        Sends the ack disconnect message.

        :param server_connection: websocket and aiohttp session created for the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        self.logger.debug("Starting send_ack_disconnect")
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        try:

            server_connection.get_auction_session().confirm_message(ack_seqno)

        except ValueError:
            # nothing was expected to be acknowledged
            pass

        # verifies the connection state
        if server_connection.state == ServerConnectionState.ESTABLISHED:

            self.logger.debug("starting to disconnect from server connection state established")
            message = self.build_ack_message(server_connection.get_auction_session().get_next_message_id(),
                                             ipap_message.get_seqno())

            await self.send_message(server_connection, message.get_message())

            self.logger.debug("disconnecting - before putting close_wait ")
            # server_connection.set_state(ServerConnectionState.CLOSE_WAIT)
            self.logger.debug("disconnecting - after putting close_wait ")

            from auction_client.auction_client_handler import HandleResourceRequestTeardown
            handle_tear_down = HandleResourceRequestTeardown(server_connection.get_auction_session().get_key())
            await handle_tear_down.start()

            self.logger.debug("disconnecting - after removing resource request ")

            message = self.build_fin_message(server_connection.get_auction_session().get_next_message_id(), 0)
            server_connection.get_auction_session().add_pending_message(message)
            await self.send_message(server_connection, message.get_message())

            self.logger.debug("disconnecting - after sending fin message ")

            server_connection.set_state(ServerConnectionState.LAST_ACK)

            self.logger.debug("ending to disconnect from server connection state established")

        # verifies the connection state
        elif server_connection.get_state() == ServerConnectionState.FIN_WAIT_2:

            # send the ack message establishing the session.
            message = self.build_ack_message(server_connection.get_auction_session().get_next_message_id(),
                                             ipap_message.get_seqno())

            await self.send_message(server_connection, message.get_message())

            await self._disconnect_socket(server_connection)
            self.auction_session_manager.del_session(server_connection.get_auction_session().get_key())
            server_connection.set_state(ServerConnectionState.CLOSED)

        else:
            # The server is not in syn sent state, so ignore the message
            self.logger.info("A msg with fin state was received,but the server is not in fin_wait state, ignoring it")

        self.logger.debug("Ending  send_ack_disconnect- new state {0}".format(str(server_connection.get_state())))

    async def handle_ack(self, server_connection: ServerConnection,
                         ipap_message: IpapMessage):
        """
        The agent received a message witn the ack flag active, it can be a auction message or a disconnect
        message

        :param server_connection: websocket and aiohttp session created for the connection
        :param ipap_message: message sent from the server.
        """
        self.logger.debug('start method handle_ack')
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        # verifies the connection state
        if server_connection.state == ServerConnectionState.FIN_WAIT_1:
            try:
                server_connection.get_auction_session().confirm_message(ack_seqno)
                server_connection.set_state(ServerConnectionState.FIN_WAIT_2)

            except ValueError:
                self.logger.info("A msg with ack nbr not expected was received, ignoring it")

        else:
            from auction_client.auction_client_handler import HandleAuctionMessage
            when = 0
            handle_auction_message = HandleAuctionMessage(server_connection, ipap_message, when)
            handle_auction_message.start()

        self.logger.debug('End method handle_ack -new state: {0}'.format(str(server_connection.get_state())))

    async def process_message(self, server_connection: ServerConnection, msg: str):
        """
        Processes a message arriving from an agent.

        :param server_connection: websocket and aiohttp session created for the connection
        :param msg: message received
        """
        try:

            ipap_message = self.is_auction_message(msg)

        except ValueError as e:
            # invalid message, we do not send anything for the moment
            self.logger.error("Invalid message from agent - Received msg: {0} - Error: {1}".format(msg, str(e)))
            return

        syn = ipap_message.get_syn()
        ack = ipap_message.get_ack()
        fin = ipap_message.get_fin()

        if syn and ack:
            print('handle_syn_ack_message')
            await self.handle_syn_ack_message(server_connection, ipap_message)

        elif fin:
            await self.send_ack_disconnect(server_connection, ipap_message)

        elif ack and (not fin and not syn):
            await self.handle_ack(server_connection, ipap_message)

        else:
            from auction_client.auction_client_handler import HandleAuctionMessage
            handle_auction_message = HandleAuctionMessage(server_connection, ipap_message, 0)
            handle_auction_message.start()

    async def process_disconnect(self, session: AuctionSession):
        """
        Teardowns the connection established for a particular session.

        :param session: session to teardown
        :return:
        """
        self.logger.debug('Starting to disconnect')

        # verifies the connection state
        if session.server_connection.state == ServerConnectionState.ESTABLISHED:

            # send the ack message establishing the session.
            message = self.build_fin_message(session.get_next_message_id(), 0)

            session.add_pending_message(message)
            await self.send_message(session.server_connection, message.get_message())

            session.server_connection.set_state(ServerConnectionState.FIN_WAIT_1)

        else:
            # The connection is not in establised state, so generate an error
            raise ValueError("Error the connection for session key {0} is not established".format(session.get_key()))

        self.logger.debug('Ending disconnect')

    async def send_message(self, server_connection: ServerConnection, message: str):
        """
        Sends the message for an agent

        :param server_connection: Server connection where we are going to sendthe message
        :param message: message to be send
        """
        self.logger.debug("start method send message")

        print('sending message')
        await server_connection.web_socket.send_str(message)

        self.logger.debug("end method send message")

    async def websocket_connect(self, use_ipv6: bool, destination_address4: ip_address,
                                destination_address6: ip_address,
                                destination_port: int, server_connection: ServerConnection):
        """
        Creates a web socket for a server connection

        :param use_ipv6: if it uses ipv 6 or not
        :param destination_address4: destination ipv6 address
        :param destination_address6: destination ipv4 address
        :param destination_port: destination port
        :param server_connection: Server connection object to be updated.
        """
        session = ClientSession()

        if use_ipv6:
            destin_ip_address = str(destination_address6)
        else:
            destin_ip_address = str(destination_address4)

        # TODO: CONNECT USING A DNS
        http_address = 'http://{ip}:{port}/{resource}'.format(ip=destin_ip_address,
                                                              port=str(destination_port),
                                                              resource='websockets')
        try:

            ws = await session.ws_connect(http_address)
            server_connection.set_web_socket(session, ws)

        except ClientConnectorError as e:
            # Close the session to clean up connections.
            await session.close()
            raise e

    async def websocket_read(self, server_connection: ServerConnection):
        """
        Reads the websocket that is related with the server connection

        :param server_connection:  server connection to read the websocket.
        :return:
        """
        try:
            async for msg in server_connection.web_socket:
                if msg.type == WSMsgType.TEXT:
                    await self.process_message(server_connection, msg.data)

                elif msg.type == WSMsgType.CLOSED:
                    self.logger.error("websocket closed by the server.")
                    print("websocket closed by the server.")
                    break

                elif msg.type == WSMsgType.ERROR:
                    self.logger.error("websocket error received.")
                    print("websocket error received.")
                    break

        except ClientConnectorError as e:
            self.logger.error("Error during server connection - error:{0}".format(str(e)))
            os.kill(os.getpid(), signal.SIGINT)
