from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import unittest
import aiounittest

from aiohttp import web

from foundation.auction_parser import AuctionXmlFileParser
from foundation.bidding_object import BiddingObject
from foundation.bidding_object_manager import BiddingObjectManager
from foundation.config import Config
from foundation.session import Session

from auction_server.server import AuctionServer
from auction_server.auction_processor import AuctionProcessor
from auction_server.auction_processor import AgentFieldSet
from auction_server.server_message_processor import ClientConnection
from auction_server.auction_server_handler import HandleClientTearDown
from auction_server.auction_server_handler import HandleRemoveBiddingObject
from auction_server.server_main_data import ServerMainData

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
        self.assertEqual(len(self.auction_processor.auctions), 1)

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
            self.auction_processor.add_bidding_object_to_auction_process(auction2.get_key(), bidding_object_2)

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

        allocations = self.auction_processor.execute_auction(auction.get_key(), datetime.now(),
                                                             datetime.now() + timedelta(seconds=10))
        self.assertEqual(len(allocations), 10)

    def test_delete_bidding_object_from_auction_process(self):
        lst_auctions = self.auction_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)
        bidding_object = BiddingObject(auction, 'bidding_obj_1', {}, {})
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
        bidding_object = BiddingObject(auction, 'bidding_obj_1', {}, {})
        self.auction_processor.add_bidding_object_to_auction_process(auction.get_key(), bidding_object)
        self.auction_processor.delete_auction_process(auction.get_key())
        self.assertEqual(len(self.auction_processor.auctions), 0)

    def test_delete_auction(self):
        lst_auctions = self.auction_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")
        auction = lst_auctions[0]
        self.auction_processor.add_auction_process(auction)
        bidding_object = BiddingObject(auction, 'bidding_obj_1', {}, {})
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


class AuctionServerHandlerTest(aiounittest.AsyncTestCase):


    async def test_handle_client_tear_down(self):

        domain = 11
        self.conf = Config('auction_server.yaml').get_config()
        module_directory = '/home/ns3/py_charm_workspace/paper_subastas/auction/proc_modules'
        self.auction_processor = AuctionProcessor(domain, module_directory)
        self.auction_xml_file_parser = AuctionXmlFileParser(domain)

        lst_auctions = self.auction_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions3.xml")

        self.auction = lst_auctions[0]
        self.auction_processor.add_auction_process(self.auction)

        self.server_main_data = ServerMainData()

        session_key = '1010'
        ip_address = '127.0.0.1'

        session = Session(session_key, ip_address, self.server_main_data.local_port,
                          '127.0.0.1', 1010, self.server_main_data.protocol)

        self.client_connection = ClientConnection(session_key)
        self.client_connection.set_session(session)

        self.bidding_manager = BiddingObjectManager(domain)

        # Parse the bidding objects in file example_bids1.xml, it allocates the memory.
        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids1.xml"
        new_bids = self.bidding_manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid = new_bids[0]
        bid.set_session(session_key)

        handle_remove_bid_1 = HandleRemoveBiddingObject(self.client_connection, bid, 10)
        handle_remove_bid_1.start()
        bid.add_task(handle_remove_bid_1)

        await self.bidding_manager.add_bidding_object(bid)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid)

        # Parse the bidding objects in file example_bids2.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids2.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid2 = new_bids[0]
        bid2.set_session(session_key)

        handle_remove_bid_2 = HandleRemoveBiddingObject(self.client_connection, bid2, 11)
        handle_remove_bid_2.start()
        bid2.add_task(handle_remove_bid_2)

        await self.bidding_manager.add_bidding_object(bid2)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid2)

        # Parse the bidding objects in file example_bids3.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids3.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid3 = new_bids[0]
        bid3.set_session(session_key)

        handle_remove_bid_3 = HandleRemoveBiddingObject(self.client_connection, bid3, 11)
        handle_remove_bid_3.start()
        bid3.add_task(handle_remove_bid_3)

        await self.bidding_manager.add_bidding_object(bid3)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid3)

        # Parse the bidding objects in file example_bids4.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids4.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid4 = new_bids[0]
        bid4.set_session(session_key)

        handle_remove_bid_4 = HandleRemoveBiddingObject(self.client_connection, bid4, 11)
        handle_remove_bid_4.start()
        bid4.add_task(handle_remove_bid_4)

        await self.bidding_manager.add_bidding_object(bid4)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid4)

        # Parse the bidding objects in file example_bids5.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids5.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid5 = new_bids[0]
        bid5.set_session(session_key)

        handle_remove_bid_5 = HandleRemoveBiddingObject(self.client_connection, bid5, 11)
        handle_remove_bid_5.start()
        bid5.add_task(handle_remove_bid_5)

        await self.bidding_manager.add_bidding_object(bid5)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid5)

        # Parse the bidding objects in file example_bids6.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids6.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid6 = new_bids[0]
        bid6.set_session("1012")
        await self.bidding_manager.add_bidding_object(bid6)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid6)

        # Parse the bidding objects in file example_bids7.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids7.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid7 = new_bids[0]
        bid7.set_session("1012")
        await self.bidding_manager.add_bidding_object(bid7)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid7)

        # Parse the bidding objects in file example_bids8.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids8.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid8 = new_bids[0]
        bid8.set_session("1012")
        await self.bidding_manager.add_bidding_object(bid8)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid8)

        # Parse the bidding objects in file example_bids9.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids9.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid9 = new_bids[0]
        bid9.set_session("1012")
        await self.bidding_manager.add_bidding_object(bid9)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid9)

        # Parse the bidding objects in file example_bids10.xml, it allocates the memory.
        manager = BiddingObjectManager(domain)

        filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids10.xml"
        new_bids = manager.parse_bidding_objects(filename)
        self.assertEqual(len(new_bids), 1)
        bid10 = new_bids[0]
        bid10.set_session("1012")
        await self.bidding_manager.add_bidding_object(bid10)
        self.auction_processor.add_bidding_object_to_auction_process(self.auction.get_key(), bid10)

        auction_process = self.auction_processor.get_auction_process(self.auction.get_key())
        bids = auction_process.get_bids()
        self.assertEqual(len(bids), 10)

        allocations = self.auction_processor.execute_auction(self.auction.get_key(), datetime.now(),
                                                             datetime.now() + timedelta(seconds=10))

        print('in test_handle_client_teardown')
        handle_client_teardown = HandleClientTearDown(self.client_connection)
        self.assertEqual(handle_client_teardown.bidding_manager.get_num_auctioning_objects(), 10)
        self.assertEqual(handle_client_teardown.auction_processor.get_number_auction_processes(), 1)
        await handle_client_teardown.start()

        self.assertEqual(handle_client_teardown.bidding_manager.get_num_auctioning_objects(), 5)
        self.assertEqual(handle_client_teardown.auction_processor.get_number_auction_processes(), 1)

        self.assertEqual(len(handle_client_teardown.auction_processor.get_auction_process(
            self.auction.get_key()).get_bids()), 5)


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
