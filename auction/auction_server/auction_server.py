from aiohttp.web import Application, run_app

from foundation.auction_manager import AuctionManager
from foundation.bidding_object_manager import BiddingObjectManager


class AuctionServer:

    def __init__(self):

        self.app = Application()
        self.auction_manager = AuctionManager()
        # self.bidding_object_manager = BiddingObjectManager()

    def run(self):
        """
        Runs the application.
        :return:
        """
        run_app(self.app)

