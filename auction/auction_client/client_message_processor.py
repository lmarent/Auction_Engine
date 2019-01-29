from aiohttp import ClientSession
from aiohttp import web, WSMsgType
from aiohttp.client_exceptions import ClientConnectorError

from foundation.auction_message_processor import AuctionMessageProcessor
import os,signal

class ClientMessageProcessor(AuctionMessageProcessor):
    """
    This class takes care of agents' communications.
    """
    def __init__(self, use_ipv6, destination_address4, destination_address6, destination_port, app):

        super(ClientMessageProcessor,self).__init__()
        self.use_ipv6 = use_ipv6
        self.destination_address4 = destination_address4
        self.destination_address6 = destination_address6
        self.destination_port  = destination_port
        self.app = app
        pass

    async def process_message(self, ws, msg : str):
        """
        Process a message arriving from an agent.

        :param ws: web socket used for communicating with the agent
        :param msg: message
        :return:
        """
        ipap_message = self.is_auction_message(msg)
        if ipap_message is not None:
            type = ipap_message.get_type()

            if type == async_create_session:

            elif type == disconnect:

            else:
                # Normal bidding message
                pass
        else:
            # invalid message, we do not send anything for the moment
            self.logger.error("Invalid message from agent with domain {}")
            pass

    async def send_message(self, message: str):
        """
        Sends the message for an agent

        :param message: message to be send
        """

    async def websocket(self):
        session = ClientSession()

        if self.use_ipv6:
            destin_ip_address = str(self.destination_address6)
        else:
           destin_ip_address = str(self.destination_address4)

        # TODO: CONNECT USING A DNS
        http_address = 'http://{ip}:{port}/{resource}'.format(ip=destin_ip_address,
                                                    port=str(self.destination_port),
                                                    resource='websockets')

        try:
            async with session.ws_connect(http_address) as ws:
                print("connected")
                self.app['session'] = session
                self.app['ws'] = ws
                async for msg in ws:
                    print(msg.type)
                    if msg.type == WSMsgType.TEXT:
                        await self.callback(msg.data)

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
