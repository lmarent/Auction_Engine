import asyncio
from asyncio import sleep
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
        self.app['server_connections'] = {}
        self.auction_session_manager = AuctionSessionManager()
        self.logger = log().get_logger()

    async def websocket_shutdown(self, server_connection: ServerConnection):
        """
        Disconnects the websocket from the server

        :param server_connection: server to disconnect
        :return:
        """
        self.logger.info('starting server connection shutdown - key {0}'.format(server_connection.key))
        # TODO: To Implement handshake shutdown.

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

    async def connect(self):
        """
        Connects a server, occurs per every resource request interval activation.
        """

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

        key = session.get_key()
        if key not in self.app['server_connections']:
            server_connection = ServerConnection(key)
            self.app['server_connections'][key] = server_connection

            await self.websocket_connect(self.client_data.use_ipv6,
                                         self.client_data.destination_address4,
                                         self.client_data.destination_address6,
                                         self.client_data.destination_port,
                                         server_connection)
            task = asyncio.ensure_future(self.websocket_read(server_connection))
            server_connection.set_task(task)
            server_connection.add_reference()
        else:
            server_connection = self.app['server_connections'][key]

        # maybe we need to wait until the connection is ready
        message = self.build_syn_message(session.get_next_message_id())
        str_msg = message.get_message()
        await self.send_message(server_connection, str_msg)
        server_connection.set_state(ServerConnectionState.SYN_SENT)
        session.add_pending_message(message)
        session.set_server_connection(server_connection)
        return session

    async def _disconnect_socket(self, session_key: str):
        """
        disconnects a session from the server.

        :param session_key: key for the session to use.
        :return:
        """
        if session_key in self.app['server_connections']:
            server_connection = self.app['server_connections'][session_key]
            server_connection.delete_reference()
            if server_connection.get_reference() == 0:
                # the shutdown of the websocket also finishes the task.
                await self.websocket_shutdown(server_connection)
                self.app['server_connections'].pop(server_connection.key)

    async def handle_syn_ack_message(self, session: AuctionSession,
                                     server_connection: ServerConnection,
                                     ipap_message: IpapMessage):
        """
        Establishes the session
        :param session:session: object that waas created to manage this connection
        :param server_connection: websocket and aiohttp session created for the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        # verifies the connection state
        if server_connection.state == ServerConnectionState.SYN_SENT:
            try:
                session.confirm_message(ack_seqno)

                # send the ack message establishing the session.
                syn_ack_message = self.build_syn_ack_message(session.get_next_message_id(), ipap_message.get_seqno())
                msg = syn_ack_message.get_message()
                await self.send_message(server_connection, msg)

            except ValueError:
                self.logger.error("Invalid ack nbr from the server, the session is going to be teardown")
                await self._disconnect_socket(session.get_key())
                self.auction_session_manager.del_session(session.get_key())

        else:
            # The server is not in syn sent state, so ignore the message
            self.logger.info("a message with syn and ack was received, but the session \
                                is not in SYN_SENT. Ignoring the message")

    async def send_ack_disconnect(self, session: AuctionSession,
                                  server_connection: ServerConnection,
                                  ipap_message: IpapMessage):
        """
        Sends the ack disconnect message.

        :param session:session: object that waas created to manage this connection
        :param server_connection: websocket and aiohttp session created for the connection
        :param ipap_message: message sent from the server.
        :return:
        """
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        # verifies the connection state
        if server_connection.state == ServerConnectionState.FIN_WAIT_2:
            try:
                session.confirm_message(ack_seqno)

                # send the ack message establishing the session.
                message = self.build_ack_message(session.get_next_message_id(), ipap_message.get_seqno())
                await self.send_message(server_connection, message.get_message())
                await self._disconnect_socket(session.get_key())
                self.auction_session_manager.del_session(session.get_key())
                server_connection.set_state(ServerConnectionState.CLOSED)

            except ValueError:
                # The message ack is not the expected, so ignore the message
                self.logger.info("A msg with ack nbr not expected was received, ignoring it")
        else:
            # The server is not in syn sent state, so ignore the message
            self.logger.info("A msg with fin state was received,but the server is not in fin_wait state, ignoring it")

    async def handle_ack(self, session: AuctionSession,
                         server_connection: ServerConnection,
                         ipap_message: IpapMessage):
        """
        The agent received a message witn the ack flag active, it can be a auction message or a disconnect
        message

        :param session:session: object that waas created to manage this connection
        :param server_connection: websocket and aiohttp session created for the connection
        :param ipap_message: message sent from the server.
        """
        self.logger.debug('start method handle_ack')
        # verifies ack sequence number
        ack_seqno = ipap_message.get_ackseqno()

        # verifies the connection state
        if server_connection.state == ServerConnectionState.FIN_WAIT_1:
            try:
                session.confirm_message(ack_seqno)
                server_connection.set_state(ServerConnectionState.FIN_WAIT_2)

            except ValueError:
                self.logger.info("A msg with ack nbr not expected was received, ignoring it")

        else:
            when = 0
            handle_auction_message = HandleAuctionMessage(session, ipap_message, when)
            handle_auction_message.start()

        self.logger.debug('End method handle_ack')

    async def process_message(self, server_connection: ServerConnection, msg: str):
        """
        Process a message arriving from an agent.

        :param server_connection: websocket and aiohttp session created for the connection
        :param msg: message received
        """
        ipap_message = self.is_auction_message(msg)
        if ipap_message is not None:
            syn = ipap_message.get_syn()
            ack = ipap_message.get_ack()
            fin = ipap_message.get_fin()
            session: AuctionSession = self.auction_session_manager.get_session(server_connection.key)
            if syn and ack:
                await self.handle_syn_ack_message(session, server_connection, ipap_message)

            elif fin:
                await self.send_ack_disconnect(session, server_connection, ipap_message)

            elif ack and (not fin and not syn):
                await self.handle_ack(session, server_connection, ipap_message)

            else:
                from auction_client.auction_client_handler import HandleAuctionMessage
                handle_auction_message = HandleAuctionMessage(session, ipap_message, 0)
                handle_auction_message.start()
        else:
            # invalid message, we do not send anything for the moment
            self.logger.error("Invalid message from agent with domain {}")

    async def process_disconnect(self, session_key: str):
        """
        Teardown the connection established for a particular session.

        :param session_key: session key to teardown
        :return:
        """
        session: AuctionSession = self.auction_session_manager.get_session(session_key)

        # verifies the connection state
        if session.server_connection.state == ServerConnectionState.ESTABLISHED:

            # send the ack message establishing the session.
            message = self.build_fin_message(session.get_next_message_id(), 0)
            await self.send_message(session.server_connection, message.get_message())
            session.server_connection.set_state(ServerConnectionState.FIN_WAIT_1)

        else:
            # The connection is not in establised state, so generate an error
            raise ValueError("Error the connection for session key {0} is not established".format(session_key))

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

    async def websocket_connect(self, use_ipv6: bool, destination_address4: ip_address, destination_address6: ip_address,
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
        ws= await session.ws_connect(http_address)
        server_connection.set_web_socket(session, ws)

    async def websocket_read(self, server_connection: ServerConnection):
        try:
            async for msg in server_connection.web_socket:
                    if msg.type == WSMsgType.TEXT:
                        print('arriving data:', msg.data)
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

    async def shutdown(self):
        """
        Shutdown the message processor, disconnects all connections.

        """
        # Close open sockets
        if 'server_connections' in self.app:
            for server_connection in self.app['server_connections']:
                await self.process_disconnect(server_connection.key)

            # Sleeps until all sockets has been closed.
            while True:
                await sleep(3)

                num_open = 0
                for server_connection in self.app['server_connections']:
                    if server_connection.state != ServerConnectionState.CLOSED:
                        num_open = num_open + 1

                if num_open == 0:
                    break
