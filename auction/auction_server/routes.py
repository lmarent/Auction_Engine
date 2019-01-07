from auction_server.views import WebSocket

routes = [
    ('POST', '/websocket',  WebSocket, 'marketplace'),
]