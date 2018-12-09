from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from auction_server.auction_server import AuctionServer

class MyAppTestCase(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        async def num_resources(request):
            return web.Response(text=str(self.auction_server.resource_manager.get_num_resources()))

        self.auction_server = AuctionServer()

        self.auction_server.app.router.add_get('/num_resources', num_resources)
        return self.auction_server.app


    # a vanilla example
    def test_example_vanilla(self):

        async def test_number_resources():
            url = "/num_resources"
            resp = await self.client.request("GET", url)
            assert resp.status == 200
            text = await resp.text()
            assert "1" in text

        self.loop.run_forever()