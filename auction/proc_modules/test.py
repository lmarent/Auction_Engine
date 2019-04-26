import unittest
from foundation.bidding_object_manager import BiddingObjectManager
from foundation.module_loader import ModuleLoader
from foundation.config import Config
from foundation.field_value import FieldValue

from datetime import datetime
from datetime import timedelta


class SubsidyAuctionTest(unittest.TestCase):

    def setUp(self):
        try:
            print('starting setup')
            self.bids = {}

            # Load the module
            module_name = "subsidy_auction"
            module_directory = Config('auction_server.yaml').get_config_param('AUMProcessor', 'ModuleDir')
            self.loader = ModuleLoader(module_directory, "AUMProcessor", module_name)

            domain = 1
            manager = BiddingObjectManager(domain)

            # Parse the bidding objects in file example_bids1.xml, it allocates the memory.
            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids1.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid = new_bids[0]
            self.bids[bid.get_key()] = bid

            # Parse the bidding objects in file example_bids2.xml, it allocates the memory.
            domain = 2
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids2.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid2 = new_bids[0]
            self.bids[bid2.get_key()] = bid2

            # Parse the bidding objects in file example_bids3.xml, it allocates the memory.
            domain = 3
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids3.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid3 = new_bids[0]
            self.bids[bid3.get_key()] = bid3

            # Parse the bidding objects in file example_bids4.xml, it allocates the memory.
            domain = 4
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids4.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid4 = new_bids[0]
            self.bids[bid4.get_key()] = bid4

            # Parse the bidding objects in file example_bids5.xml, it allocates the memory.
            domain = 5
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids5.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid5 = new_bids[0]
            self.bids[bid5.get_key()] = bid5

            # Parse the bidding objects in file example_bids6.xml, it allocates the memory.
            domain = 6
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids6.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid6 = new_bids[0]
            self.bids[bid6.get_key()] = bid6

            # Parse the bidding objects in file example_bids7.xml, it allocates the memory.
            domain = 7
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids7.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid7 = new_bids[0]
            self.bids[bid7.get_key()] = bid7

            # Parse the bidding objects in file example_bids8.xml, it allocates the memory.
            domain = 8
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids8.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid8 = new_bids[0]
            self.bids[bid8.get_key()] = bid8

            # Parse the bidding objects in file example_bids9.xml, it allocates the memory.
            domain = 9
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids9.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid9 = new_bids[0]
            self.bids[bid9.get_key()] = bid9

            # Parse the bidding objects in file example_bids10.xml, it allocates the memory.
            domain = 10
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids10.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid10 = new_bids[0]
            self.bids[bid10.get_key()] = bid10

            self.assertEqual(len(self.bids), 10)

            print('ending setup')
        except Exception as e:
            print(str(e))

    def test_not_enough_quantities(self):
        print('in test_not_enough_quantities')
        auction_key = "1.1"
        start = datetime.now()
        stop = start + timedelta(seconds=100)

        module = self.loader.get_module("subsidy_auction")

        if module:
            params = {}
            # The following are the required parameters
            config_param_1 = FieldValue(name="bandwidth")
            config_param_1.parse_field_value("40")
            params["bandwidth"] = config_param_1

            config_param_2 = FieldValue(name="subsidy")
            config_param_2.parse_field_value("1.2")
            params["subsidy"] = config_param_2

            config_param_3 = FieldValue(name="maxvalue01")
            config_param_3.parse_field_value("0.5")
            params["maxvalue01"] = config_param_3

            config_param_4 = FieldValue(name="reserveprice")
            config_param_4.parse_field_value("0.15")
            params["reserveprice"] = config_param_4

            tot_demand = module.proc_module.calculate_requested_quantities(self.bids)
            self.assertEqual(tot_demand, 85)

            allocations = module.execute(params, auction_key, start, stop, self.bids)
            self.assertEqual(len(allocations), 10)

            qty_allocated = 0
            for allocation in allocations:
                qty_allocated += module.proc_module.get_allocation_quantity(allocation)

            self.assertEqual(qty_allocated, 40)

            for allocation in allocations:
                sell_price = module.proc_module.get_bid_price(allocation)
                break

            self.assertEqual(sell_price, 0.456)

    def test_enough_quantities(self):
        print('in test_enough_quantities')
        auction_key = "1.1"
        start = datetime.now()
        stop = start + timedelta(seconds=100)

        module = self.loader.get_module("subsidy_auction")
        if module:
            # The following are the required parameters
            params = {}
            # The following are the required parameters
            config_param_1 = FieldValue(name="bandwidth")
            config_param_1.parse_field_value("90")
            params["bandwidth"] = config_param_1

            config_param_2 = FieldValue(name="subsidy")
            config_param_2.parse_field_value("1.2")
            params["subsidy"] = config_param_2

            config_param_3 = FieldValue(name="maxvalue01")
            config_param_3.parse_field_value("0.5")
            params["maxvalue01"] = config_param_3

            config_param_4 = FieldValue(name="reserveprice")
            config_param_4.parse_field_value("0.15")
            params["reserveprice"] = config_param_4

            allocations = module.execute(params, auction_key, start, stop, self.bids)
            self.assertEqual(len(allocations), 10)

            qty_allocated = 0
            for allocation in allocations:
                qty_allocated += module.proc_module.get_allocation_quantity(allocation)

            self.assertEqual(qty_allocated, 73)

            for allocation in allocations:
                sell_price = module.proc_module.get_bid_price(allocation)
                break

            self.assertEqual(sell_price, 0.15)


class BasicModuleTest(unittest.TestCase):

    def setUp(self):
        try:
            print('starting setup')
            self.bids = {}

            # Load the module
            module_name = "basic_module"
            module_directory = Config('auction_server.yaml').get_config_param('AUMProcessor', 'ModuleDir')
            self.loader = ModuleLoader(module_directory, "AUMProcessor", module_name)

            domain = 1
            manager = BiddingObjectManager(domain)

            # Parse the bidding objects in file example_bids1.xml, it allocates the memory.
            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids1.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid = new_bids[0]
            self.bids[bid.get_key()] = bid

            # Parse the bidding objects in file example_bids2.xml, it allocates the memory.
            domain = 2
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids2.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid2 = new_bids[0]
            self.bids[bid2.get_key()] = bid2

            # Parse the bidding objects in file example_bids3.xml, it allocates the memory.
            domain = 3
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids3.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid3 = new_bids[0]
            self.bids[bid3.get_key()] = bid3

            # Parse the bidding objects in file example_bids4.xml, it allocates the memory.
            domain = 4
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids4.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid4 = new_bids[0]
            self.bids[bid4.get_key()] = bid4

            # Parse the bidding objects in file example_bids5.xml, it allocates the memory.
            domain = 5
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids5.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid5 = new_bids[0]
            self.bids[bid5.get_key()] = bid5

            # Parse the bidding objects in file example_bids6.xml, it allocates the memory.
            domain = 6
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids6.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid6 = new_bids[0]
            self.bids[bid6.get_key()] = bid6

            # Parse the bidding objects in file example_bids7.xml, it allocates the memory.
            domain = 7
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids7.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid7 = new_bids[0]
            self.bids[bid7.get_key()] = bid7

            # Parse the bidding objects in file example_bids8.xml, it allocates the memory.
            domain = 8
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids8.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid8 = new_bids[0]
            self.bids[bid8.get_key()] = bid8

            # Parse the bidding objects in file example_bids9.xml, it allocates the memory.
            domain = 9
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids9.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid9 = new_bids[0]
            self.bids[bid9.get_key()] = bid9

            # Parse the bidding objects in file example_bids10.xml, it allocates the memory.
            domain = 10
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids10.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid10 = new_bids[0]
            self.bids[bid10.get_key()] = bid10

            self.assertEqual(len(self.bids), 10)

            print('ending setup')
        except Exception as e:
            print(str(e))

    def test_not_enough_quantities(self):
        print('in test_not_enough_quantities')
        auction_key = "1.1"
        start = datetime.now()
        stop = start + timedelta(seconds=100)

        module = self.loader.get_module("basic_module")

        if module:
            params = {}
            # The following are the required parameters
            config_param_1 = FieldValue(name="bandwidth")
            config_param_1.parse_field_value("40")
            params["bandwidth"] = config_param_1

            config_param_2 = FieldValue(name="subsidy")
            config_param_2.parse_field_value("1.2")
            params["subsidy"] = config_param_2

            config_param_3 = FieldValue(name="maxvalue01")
            config_param_3.parse_field_value("0.5")
            params["maxvalue01"] = config_param_3

            config_param_4 = FieldValue(name="reserveprice")
            config_param_4.parse_field_value("0.15")
            params["reserveprice"] = config_param_4

            tot_demand = module.proc_module.calculate_requested_quantities(self.bids)
            self.assertEqual(tot_demand, 85)

            allocations = module.execute(params, auction_key, start, stop, self.bids)
            self.assertEqual(len(allocations), 10)

            qty_allocated = 0
            for allocation in allocations:
                qty_allocated += module.proc_module.get_allocation_quantity(allocation)

            self.assertEqual(qty_allocated, 40)

            for allocation in allocations:
                sell_price = module.proc_module.get_bid_price(allocation)
                break

            self.assertEqual(sell_price, 0.38)

            sell_prices = []
            qty_allocates = []
            bid_ids = []
            revenue = 0
            for allocation in allocations:
                qty = module.proc_module.get_allocation_quantity(allocation)
                sell_price = module.proc_module.get_bid_price(allocation)
                bid_id = allocation.get_parent_key()
                revenue = revenue + (qty*sell_price)
                sell_prices.append(sell_price)
                qty_allocates.append(qty)
                bid_ids.append(bid_id)

            print(sell_prices)
            print(qty_allocates)
            print(bid_ids)

    def test_enough_quantities(self):
        print('in test_enough_quantities')
        auction_key = "1.1"
        start = datetime.now()
        stop = start + timedelta(seconds=100)

        module = self.loader.get_module("basic_module")
        if module:
            # The following are the required parameters
            params = {}
            # The following are the required parameters
            config_param_1 = FieldValue(name="bandwidth")
            config_param_1.parse_field_value("90")
            params["bandwidth"] = config_param_1

            config_param_2 = FieldValue(name="subsidy")
            config_param_2.parse_field_value("1.2")
            params["subsidy"] = config_param_2

            config_param_3 = FieldValue(name="maxvalue01")
            config_param_3.parse_field_value("0.5")
            params["maxvalue01"] = config_param_3

            config_param_4 = FieldValue(name="reserveprice")
            config_param_4.parse_field_value("0.15")
            params["reserveprice"] = config_param_4

            allocations = module.execute(params, auction_key, start, stop, self.bids)
            self.assertEqual(len(allocations), 10)

            qty_allocated = 0
            for allocation in allocations:
                qty_allocated += module.proc_module.get_allocation_quantity(allocation)

            self.assertEqual(qty_allocated, 73)

            for allocation in allocations:
                sell_price = module.proc_module.get_bid_price(allocation)
                break

            self.assertEqual(sell_price, 0.15)


class TwoAuctionPerfectInformationTest(unittest.TestCase):

    def setUp(self):
        try:
            print('starting setup')
            self.bids = {}

            # Load the module
            module_name = "two_auction_perfect_information"
            module_directory = Config('auction_server.yaml').get_config_param('AUMProcessor', 'ModuleDir')
            self.loader = ModuleLoader(module_directory, "AUMProcessor", module_name)

            domain = 1
            manager = BiddingObjectManager(domain)

            # Parse the bidding objects in file example_bids1.xml, it allocates the memory.
            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids1.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid = new_bids[0]
            self.bids[bid.get_key()] = bid

            # Parse the bidding objects in file example_bids2.xml, it allocates the memory.
            domain = 2
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids2.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid2 = new_bids[0]
            self.bids[bid2.get_key()] = bid2

            # Parse the bidding objects in file example_bids3.xml, it allocates the memory.
            domain = 3
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids3.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid3 = new_bids[0]
            self.bids[bid3.get_key()] = bid3

            # Parse the bidding objects in file example_bids4.xml, it allocates the memory.
            domain = 4
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids4.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid4 = new_bids[0]
            self.bids[bid4.get_key()] = bid4

            # Parse the bidding objects in file example_bids5.xml, it allocates the memory.
            domain = 5
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids5.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid5 = new_bids[0]
            self.bids[bid5.get_key()] = bid5

            # Parse the bidding objects in file example_bids6.xml, it allocates the memory.
            domain = 6
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids6.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid6 = new_bids[0]
            self.bids[bid6.get_key()] = bid6

            # Parse the bidding objects in file example_bids7.xml, it allocates the memory.
            domain = 7
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids7.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid7 = new_bids[0]
            self.bids[bid7.get_key()] = bid7

            # Parse the bidding objects in file example_bids8.xml, it allocates the memory.
            domain = 8
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids8.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid8 = new_bids[0]
            self.bids[bid8.get_key()] = bid8

            # Parse the bidding objects in file example_bids9.xml, it allocates the memory.
            domain = 9
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids9.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid9 = new_bids[0]
            self.bids[bid9.get_key()] = bid9

            # Parse the bidding objects in file example_bids10.xml, it allocates the memory.
            domain = 10
            manager = BiddingObjectManager(domain)

            filename = "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_generalized_bids10.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids), 1)
            bid10 = new_bids[0]
            self.bids[bid10.get_key()] = bid10

            self.assertEqual(len(self.bids), 10)

            print('ending setup')
        except Exception as e:
            print(str(e))

    def test_not_enough_quantities(self):
        print('in test_not_enough_quantities')
        auction_key = "1.1"
        start = datetime.now()
        stop = start + timedelta(seconds=100)

        module = self.loader.get_module("two_auction_perfect_information")

        if module:
            params = {}
            # The following are the required parameters
            config_param_1 = FieldValue(name="bandwidth01")
            config_param_1.parse_field_value("20")
            params["bandwidth01"] = config_param_1

            config_param_2 = FieldValue(name="bandwidth02")
            config_param_2.parse_field_value("30")
            params["bandwidth02"] = config_param_2

            config_param_3 = FieldValue(name="reserveprice01")
            config_param_3.parse_field_value("0.15")
            params["reserveprice01"] = config_param_3

            config_param_4 = FieldValue(name="reserveprice02")
            config_param_4.parse_field_value("0.5")
            params["reserveprice02"] = config_param_4

            config_param_5 = FieldValue(name="maxvalue01")
            config_param_5.parse_field_value("0.5")
            params["maxvalue01"] = config_param_5

            config_param_6 = FieldValue(name="maxvalue02")
            config_param_6.parse_field_value("0.9")
            params["maxvalue02"] = config_param_6

            tot_demand = module.proc_module.calculate_requested_quantities(self.bids)
            self.assertEqual(tot_demand, 85)

            allocations = module.execute(params, auction_key, start, stop, self.bids)
            self.assertEqual(len(allocations), 10)

            qty_allocated = 0
            for allocation in allocations:
                qty_allocated += module.proc_module.get_allocation_quantity(allocation)

            self.assertEqual(qty_allocated, 50)

            sell_prices = []
            qty_allocates = []
            bid_ids = []
            revenue = 0
            for allocation in allocations:
                qty = module.proc_module.get_allocation_quantity(allocation)
                sell_price = module.proc_module.get_bid_price(allocation)
                bid_id = allocation.get_parent_key()
                revenue = revenue + (qty*sell_price)
                sell_prices.append(sell_price)
                qty_allocates.append(qty)
                bid_ids.append(bid_id)

            print(sell_prices)
            print(qty_allocates)
            print(bid_ids)

            # for allocation in allocations:
            #    sell_price = module.proc_module.get_bid_price(allocation)
            #    break

            # self.assertEqual(sell_price, 0.38)

    def test_enough_quantities(self):
        print('in test_enough_quantities')
        auction_key = "1.1"
        start = datetime.now()
        stop = start + timedelta(seconds=100)

        module = self.loader.get_module("two_auction_perfect_information")
        if module:
            params = {}
            # The following are the required parameters
            config_param_1 = FieldValue(name="bandwidth01")
            config_param_1.parse_field_value("45")
            params["bandwidth01"] = config_param_1

            config_param_2 = FieldValue(name="bandwidth02")
            config_param_2.parse_field_value("45")
            params["bandwidth02"] = config_param_2

            config_param_3 = FieldValue(name="reserveprice01")
            config_param_3.parse_field_value("0.15")
            params["reserveprice01"] = config_param_3

            config_param_4 = FieldValue(name="reserveprice02")
            config_param_4.parse_field_value("0.5")
            params["reserveprice02"] = config_param_4

            config_param_5 = FieldValue(name="maxvalue01")
            config_param_5.parse_field_value("0.5")
            params["maxvalue01"] = config_param_5

            config_param_6 = FieldValue(name="maxvalue02")
            config_param_6.parse_field_value("0.9")
            params["maxvalue02"] = config_param_6

            allocations = module.execute(params, auction_key, start, stop, self.bids)
            self.assertEqual(len(allocations), 10)

            qty_allocated = 0
            for allocation in allocations:
                qty_allocated += module.proc_module.get_allocation_quantity(allocation)

            self.assertEqual(qty_allocated, 73)

            # for allocation in allocations:
            #    sell_price = module.proc_module.get_bid_price(allocation)
            #    break

            # self.assertEqual(sell_price, 0.15)
