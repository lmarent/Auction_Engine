from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType
from aiohttp import WSCloseCode

from python_wrapper.ipap_message import IpapMessage

class MessageProcessor:
    """
    This class take cares of agents' communications.
    """
    def __init__(self):
        pass

    def is_auction_message(self, msg: str) -> IpapMessage:
        """
        Establishes whether the given message is a valid auction message.

        :param msg: message to verify
        :return: An IpapMessage if it is a valid message, None otherwise.
        """
        # parse the message
        ipap_message = IpapMessage()
        ret = ipap_message.ipap_import(msg)

        if ret:
            # if the parsing could be done, then it is valid auction message
            return ipap_message
        else:
            # else is not a valid message.
            return None

    async def process_message(self, ws, msg : str):
        """
        Process a message arriving from an agent.

        :param ws: web socket used for communicating with the agent
        :param msg: message
        :return:
        """
        ipap_message = self.is_auction_message(msg):
        if ipap_message is not None:
            type = ipap_message.get_type()

            if type == create_session:

            elif type == bidding_process:

            elif type == disconnect:

            else:
                # invalid message, we do not send anything.
                pass
        else:
            # invalid message, we do not send anything for the moment
            self.logger.info("Invalid message from agent with domain {}")
            pass

    async def send_message(self, message: str):
        """
        Sends the message for an agent

        :param message: message to be send
        """


    async def handle_web_socket(self, request):
        """
        Handles a new arriving web socket

        :param request: request received.
        :return:
        """
        ws = WebSocketResponse()
        await ws.prepare(request)

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
