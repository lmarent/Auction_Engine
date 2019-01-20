from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType
from aiohttp import WSCloseCode


class MessageProcessor:
    """
    This class take cares of agents' communications.
    """
    def __init__(self):
        pass

    async def process_message(self, msg):
        print(msg)

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
                    await self.process_message(msg)

                elif msg.type == WSMsgType.error:
                    self.logger.debug('ws connection closed with exception %s' % ws.exception())

                elif msg.type == WSMsgType.close:
                    self.logger.debug('ws connection closed')
        finally:
            request.app['web_sockets'].remove(ws)

        self.logger.debug('websocket connection closed')
        return ws
