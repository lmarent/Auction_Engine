from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import unittest

from aiohttp import web
from auction_server.server import AuctionServer
from auction_server.auction_processor import AuctionProcessor
from foundation.auction_parser import AuctionXmlFileParser
from foundation.bidding_object import BiddingObject
from foundation.bidding_object_manager import BiddingObjectManager
from foundation.config import Config
from auction_server.auction_processor import AgentFieldSet
from datetime import datetime
from datetime import timedelta

class AuctionProcessorTest(unittest.TestCase):

    def setUp(self):
        domain = 10
        self.conf = Config('auction_server.yaml').get_config()
        module_directory = '/home/ns3/py_charm_workspace/paper_subastas/auction/proc_modules'
        self.auction_processor = AuctionProcessor(domain, module_directory)
        self.auction_xml_file_parser = AuctionXmlFileParser(domain)

    def test_add_auction_process(self):

        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)
        self.assertEqual(len(self.auction_processor.auctions),1)

        # test invalid module defined in the auction
        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions1.xml")
        auction2 = lst_auctions[0]
        key = self.auction_processor.add_auction_process(auction2)
        self.assertEqual(key, None)

    def test_add_bidding_object_to_auction_process(self):
        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)

        domain = 1
        manager = BiddingObjectManager(domain)

        # Parse the bidding objects in file example_bids1.xml, it allocates the memory.
        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids1.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid)

        # Parse the bidding objects in file example_bids2.xml, it allocates the memory.
        domain = 2
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids2.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid2 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid2)

        # Parse the bidding objects in file example_bids3.xml, it allocates the memory.
        domain = 3
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids3.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid3 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid3)

        # Parse the bidding objects in file example_bids4.xml, it allocates the memory.
        domain = 4
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids4.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid4 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid4)

        # Parse the bidding objects in file example_bids5.xml, it allocates the memory.
        domain = 5
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids5.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid5 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid5)

        # Parse the bidding objects in file example_bids6.xml, it allocates the memory.
        domain = 6
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids6.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid6 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid6)

        # Parse the bidding objects in file example_bids7.xml, it allocates the memory.
        domain = 7
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids7.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid7 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid7)

        # Parse the bidding objects in file example_bids8.xml, it allocates the memory.
        domain = 8
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids8.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid8 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid8)

        # Parse the bidding objects in file example_bids9.xml, it allocates the memory.
        domain = 9
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids9.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid9 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid9)

        # Parse the bidding objects in file example_bids10.xml, it allocates the memory.
        domain = 10
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids10.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid10 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid10)

        auction_process = self.auction_processor.get_auction_process(auction.get_key())
        bids = auction_process.get_bids()
        self.assertEqual(len(bids), 10)

        # test wrong bidding object- auction is not as an auction process.
        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions1.xml")
        auction2 = lst_auctions[0]
        bidding_object_2 = BiddingObject(auction2, 'bidding_obj_2', {}, {})
        with self.assertRaises(ValueError):
            self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bidding_object_2)

        with self.assertRaises(ValueError):
            self.auction_processor.add_bidding_object_to_auction_process(auction2.get_key(), bidding_object)


    def test_execute_auction(self):
        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)

        domain = 1
        manager = BiddingObjectManager(domain)

        # Parse the bidding objects in file example_bids1.xml, it allocates the memory.
        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids1.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid)

        # Parse the bidding objects in file example_bids2.xml, it allocates the memory.
        domain = 2
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids2.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid2 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid2)

        # Parse the bidding objects in file example_bids3.xml, it allocates the memory.
        domain = 3
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids3.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid3 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid3)

        # Parse the bidding objects in file example_bids4.xml, it allocates the memory.
        domain = 4
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids4.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid4 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid4)

        # Parse the bidding objects in file example_bids5.xml, it allocates the memory.
        domain = 5
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids5.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid5 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid5)

        # Parse the bidding objects in file example_bids6.xml, it allocates the memory.
        domain = 6
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids6.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid6 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid6)

        # Parse the bidding objects in file example_bids7.xml, it allocates the memory.
        domain = 7
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids7.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid7 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid7)

        # Parse the bidding objects in file example_bids8.xml, it allocates the memory.
        domain = 8
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids8.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid8 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid8)

        # Parse the bidding objects in file example_bids9.xml, it allocates the memory.
        domain = 9
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids9.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid9 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid9)

        # Parse the bidding objects in file example_bids10.xml, it allocates the memory.
        domain = 10
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids10.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid10 = new_bids[0]
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bid10)

        auction_process = self.auction_processor.get_auction_process(auction.get_key())
        bids = auction_process.get_bids()
        self.assertEqual(len(bids), 10)

        allocations = self.auction_processor.execute_auction(auction.get_key(),datetime.now(),
                                                             datetime.now() + timedelta(seconds=10))
        self.assertEqual(len(allocations), 10)

    def test_delete_bidding_object_from_auction_process(self):
        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)
        bidding_object = BiddingObject(auction,'bidding_obj_1', {},{})
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bidding_object)
        self.auction_processor.delete_bidding_object_from_auction_process(auction.get_key(), bidding_object)
        auction_process = self.auction_processor.get_auction_process(auction.get_key())
        bids = auction_process.get_bids()
        self.assertEqual(len(bids), 0)

    def test_delete_auction_process(self):
        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)
        bidding_object = BiddingObject(auction,'bidding_obj_1', {},{})
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bidding_object)
        self.auction_processor.delete_auction_process(auction.get_key())
        self.assertEqual(len(self.auction_processor.auctions), 0)

    def test_delete_auction(self):
        lst_auctions = self.auction_xml_file_parser.parse(
                "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)
        bidding_object = BiddingObject(auction,'bidding_obj_1', {},{})
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bidding_object)
        self.auction_processor.delete_auction(auction)
        self.assertEqual(len(self.auction_processor.auctions), 0)

    def test_get_set_field(self):
        set_name = AgentFieldSet.SESSION_FIELD_SET_NAME
        set1 = self.auction_processor.get_set_field(set_name)
        self.assertEqual(len(set1), 4)

        set_name = AgentFieldSet.REQUEST_FIELD_SET_NAME
        set2 = self.auction_processor.get_set_field(set_name)
        self.assertEqual(len(set2), 3)


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
