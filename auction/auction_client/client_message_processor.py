from aiohttp import ClientSession
from aiohttp import web, WSMsgType
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp import WSCloseCode

from ipaddress import ip_address
import os, signal
from enum import Enum

from foundation.auction_message_processor import AuctionMessageProcessor

from auction_client.auction_session_manager import AuctionSessionManager
from auction_client.client_main_data import ClientMainData
from auction_client.auction_session import AuctionSession
from python_wrapper.ipap_message import IpapMessage

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


class ClientMessageProcessor(AuctionMessageProcessor):
    """
    This class takes care of agents' communications.
    """

    def __init__(self, app, domain: int):

        super(ClientMessageProcessor, self).__init__(domain)
        self.app = app
        self.app['server_connections'] = {}
        self.key_separator = '|'
        self.auction_session_manager = AuctionSessionManager()
        self.client_data = ClientMainData()
        pass

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

        if self.use_ipv6:
            session = self.auction_session_manager.create_agent_session(self.client_data.ip_address6,
                                                                        self.client_data.destination_address6,
                                                                        self.client_data.source_port,
                                                                        self.client_data.destination_port,
                                                                        self.client_data.protocol,
                                                                        self.client_data.life_time)
        else:
            session = self.auction_session_manager.create_agent_session(self.client_data.ip_address4,
                                                                        self.client_data.destination_address4,
                                                                        self.client_data.source_port,
                                                                        self.client_data.destination_port,
                                                                        self.client_data.protocol,
                                                                        self.client_data.life_time)

        key = session.get_key()
        server_connection = None

        if key not in self.app['server_connections']:
            server_connection = ServerConnection(key)
            self.app['server_connections'][key] = server_connection
            task = self.app.loop.create_task(self.websocket(self.client_data.use_ipv6,
                                                            self.client_data.destination_address4,
                                                            self.client_data.destination_address6,
                                                            self.client_data.destination_port,
                                                            server_connection))
            server_connection.set_task(task)
            server_connection.add_reference()
        else:
            server_connection = self.app['server_connections'][key]

        message = self.build_syn_message(session.get_next_message_id())
        self.send_message(server_connection, message.get_message())
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

    async def establish_session(self, session: AuctionSession,
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
                message = self.build_syn_ack_message(session.get_next_message_id(), ipap_message.get_seqno())
                self.send_message(server_connection, message.get_message())

            except ValueError as e:
                logger.error("Invalid ack nbr from the server, the session is going to be teardown")
                self._disconnect_socket(session.get_key())
                self.auction_session_manager.del_session(session.get_key())

        else:
            # The server is not in syn sent state, so ignore the message
            pass

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
                self.send_message(server_connection, message.get_message())
                self._disconnect_socket(session.get_key())
                self.auction_session_manager.del_session(session.get_key())

            except ValueError as e:
                # The message ack is not the expected, so ignore the message
                pass
        else:
            # The server is not in syn sent state, so ignore the message
            pass

    async def process_message(self, server_connection: ServerConnection, msg: str):
        """
        Process a message arriving from an agent.

        :param ws: web socket used for communicating with the agent
        :param msg: message
        :return:
        """
        ipap_message = self.is_auction_message(msg)
        if ipap_message is not None:
            syn = ipap_message.get_syn()
            ack = ipap_message.get_ack()
            fin = ipap_message.get_fin()
            session = self.auction_session_manager.get(server_connection.key)
            if syn and ack:
                self.establish_session(session, ipap_message)

            elif fin:
                self.send_ack_disconnect()

            else:
                handle_auction_message = HandleAuctionMessage(ipap_message, 0)
                handle_auction_message.start()
                pass
        else:
            # invalid message, we do not send anything for the moment
            self.logger.error("Invalid message from agent with domain {}")
            pass

    async def process_disconnect(self, session_key: str):
        """
        Teardown the connection established for a particular session.

        :param session_key: session key to teardown
        :return:
        """
        session = self.auction_session_manager.get_session(session_key)

        # verifies the connection state
        if session.server_connection.state == ServerConnectionState.ESTABLISHED:

            # send the ack message establishing the session.
            message = self.build_fin_message(session.get_next_message_id(), 0 )
            self.send_message(session.server_connection, message.get_message())
            session.server_connection.set_state(ServerConnectionState.FIN_WAIT_1)

        else:
            # The connection is not in establised state, so generate an error
            raise ValueError("Error the connection for session key {0} is not established".format(session_key))

    async def send_message(self, server_connection: ServerConnection, message: str):
        """
        Sends the message for an agent

        :param message: message to be send
        """
        server_connection.web_socket.send_str(message)

    async def websocket(self, use_ipv6: bool, destination_address4: ip_address, destination_address6: ip_address,
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
            async with session.ws_connect(http_address) as ws:
                server_connection.set_web_socket(session, ws)
                async for msg in ws:
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

            print("closed by server request")
            os.kill(os.getpid(), signal.SIGINT)

        except ClientConnectorError as e:
            print(str(e))
            self.logger.error("Error during server connection - error:{0}".format(str(e)))
            os.kill(os.getpid(), signal.SIGINT)
