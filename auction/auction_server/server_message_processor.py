from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType

from foundation.auction_message_processor import AuctionMessageProcessor

class ServerMessageProcessor(AuctionMessageProcessor):
    """
    This class takes care of agents' communications.
    """
    def __init__(self):

        super(ServerMessageProcessor,self).__init__()
        pass


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

            if type == sync_session:

            elif type == ack_sync_session:

            elif type == disconnect:

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
