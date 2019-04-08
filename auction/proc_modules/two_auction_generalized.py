from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.config_param import ConfigParam
from foundation.bidding_object import BiddingObject
from foundation.auction import AuctioningObjectType
from foundation.module import ModuleInformation
from foundation.parse_format import ParseFormats

from proc_modules.proc_module import ProcModule
from proc_modules.proc_module import AllocProc

from math import floor
import random
from utils.auction_utils import log
from typing import List
from typing import Dict
from typing import DefaultDict
from datetime import datetime
from collections import defaultdict


class TwoAuctionGeneralized(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(TwoAuctionGeneralized, self).__init__(module_name, module_file, module_handle, config_group)
        self.config_params = {}
        self.logger = log().get_logger()
        self.bandwidth = 0
        self.reserved_price = 0
        self.domain = 0
        self.proc_module = ProcModule()

    def init_module(self, config_params: Dict[str, ConfigParam]):
        """
        Initializes the module

        :param config_params: dictionary with the given configuration parameters
        """
        self.logger.debug('in init_module')
        self.config_params = config_params
        self.domain = config_params['domainid']

    @staticmethod
    def make_key(auction_key: str, bid_key: str) -> str:
        """
        Make the key of an allocation from the auction key and bidding object key

        :param auction_key: auction key
        :param bid_key: bidding object key
        :return:
        """
        return auction_key + '-' + bid_key

    def destroy_module(self):
        """
        method to be executed when destroying the class
        :return:
        """
        self.logger.debug('in destroy_module')

    def create_allocation(self, session_id: str, auction_key: str, start: datetime,
                          stop: datetime, quantity: float, price: float) -> BiddingObject:
        """
        Creates a new allocation

        :param session_id: session id to be associated
        :param auction_key: auction key
        :param start: allocation's start
        :param stop: allocation's stop
        :param quantity: quantity to assign
        :param price: price to pay
        :return: Bidding object
        """
        self.logger.debug("bas module: start create allocation")

        elements = dict()
        config_elements = dict()

        # Insert quantity ipap_field
        record_id = "record_1"
        self.proc_module.insert_string_field("recordid", record_id, config_elements)
        self.proc_module.insert_float_field("quantity", quantity, config_elements)
        self.proc_module.insert_double_field("unitprice", price, config_elements)
        elements[record_id] = config_elements

        # construct the interval with the allocation, based on start datetime
        # and interval for the requesting auction

        options = dict()
        option_id = 'option_1'
        config_options = dict()

        self.proc_module.insert_string_field("recordid", option_id, config_elements)
        self.proc_module.insert_datetime_field("start", start, config_options)
        self.proc_module.insert_datetime_field("stop", stop, config_options)
        options[option_id] = config_options

        bidding_object_id = self.proc_module.get_bidding_object_id()
        bidding_object_key = str(self.domain) + '.' + bidding_object_id
        alloc = BiddingObject(auction_key, bidding_object_key, AuctioningObjectType.ALLOCATION, elements, options)

        # All objects must be inherit the session from the bid.
        alloc.set_session(session_id)

        return alloc

    @staticmethod
    def get_probability() -> float:
        return random.uniform(0, 1)


    def create_request(self, bids_low: Dict[str, BiddingObject], bids_high: Dict[str, BiddingObject],
                       q_star: float) -> (DefaultDict[int, list], DefaultDict[float, list], int, int):
        """

        :param self:
        :param bids_low:
        :param bids_high:
        :param q_star:
        :return:
        """
        self.logger.debug("create requests")

        nhtmp = 0
        nltmp = 0

        # creates the request for the L auction.
        index = 0
        low_auction_allocs: DefaultDict[float, list] = defaultdict(list)
        for bidding_object_key in bids_low:
            bidding_object = bids_low[bidding_object_key]
            elements = bidding_object.elements
            inserted = False
            for element_name in elements:
                config_params = elements[element_name]
                price = ParseFormats.parse_float(config_params["unitprice"].value)
                quantity = ParseFormats.parse_float(config_params["quantity"].value)

                if quantity > 0:
                    alloc = AllocProc(bidding_object.get_auction_key(), bidding_object.get_key(),
                                      element_name, bidding_object.get_session(), quantity, price)
                    low_auction_allocs[index].append(alloc)
                    nltmp = nltmp + quantity
                    inserted = True

            # Only increase index if there was another node inserted.
            if inserted:
                index = index + 1

        self.logger.debug("create requests after low budget bids")

        # go through all high budget bids and pass some of their units as low auction requests.
        high_auction_allocs: DefaultDict[float, list] = defaultdict(list)
        for bidding_object_key in bids_high:
            alloc_bids = []
            bidding_object = bids_high[bidding_object_key]
            elements = bidding_object.elements
            inserted = False
            for element_name in elements:
                config_params = elements[element_name]
                price = ParseFormats.parse_float(config_params["unitprice"].value)
                quantity = ParseFormats.parse_float(config_params["quantity"].value)
                units_to_pass = 0
                for k in range(0, floor(quantity)):
                    if self.get_probability() <= q_star:  # pass a unit.
                        units_to_pass = units_to_pass + 1

                # quantities in the H auction.
                alloc1 = AllocProc(bidding_object.get_auction_key(), bidding_object.get_key(),
                                   element_name, bidding_object.get_session(), quantity, price)

                high_auction_allocs[price].append(alloc1)
                nhtmp = nhtmp + quantity - units_to_pass

                # quantities in the L auction.
                alloc2 = AllocProc(bidding_object.get_auction_key(), bidding_object.get_key(),
                                   element_name, bidding_object.get_session(), units_to_pass, price)
                alloc_bids.append(alloc2)
                inserted = True

                self.logger.debug("bid set: {0} units pass: {1}".format(bidding_object.get_key(), str(units_to_pass)))
                nltmp = nltmp + units_to_pass

            # Only increase index if there was another node inserted.
            if inserted:
                low_auction_allocs[index].append(alloc_bids)
                index = index + 1

        nl = nltmp
        nh = nhtmp

        self.logger.debug("ending create requests -nl: {0} nh: {1}".format(str(nl), str(nh)))
        return low_auction_allocs, high_auction_allocs, nl, nh

    def execute_auction_random_allocation(self, reserved_price_low: float, start: datetime, stop: datetime,
                                          bids_to_fulfill: DefaultDict[int, list], qty_available: float) -> dict:
        """

        :param reserved_price_low:
        :param start:
        :param stop:
        :param bids_to_fulfill:
        :param qty_available:
        :return:
        """
        self.logger.debug("execute Action random allocation")

        allocations = {}

        # Create allocations with zero quantity for bids that are below the reserved price.
        sorted_indexes: List[int] = sorted(bids_to_fulfill.keys(), reverse=True)
        for index in sorted_indexes:
            self.logger.debug("execute action random allocation 1")
            sorted_bids = bids_to_fulfill[index]
            for bid_index in range(len(sorted_bids) - 1, -1, -1):
                if sorted_bids[bid_index].original_price < reserved_price_low:
                    key = self.make_key(sorted_bids[bid_index].auction_key, sorted_bids[bid_index].bidding_object_key)
                    if key not in allocations:
                        allocation = self.create_allocation(sorted_bids[bid_index].session_id,
                                                            sorted_bids[bid_index].auction_key, start,
                                                            stop, 0, reserved_price_low)

                        allocations[key] = allocation

                    original_price = sorted_bids[bid_index].original_price
                    self.logger.debug("execute Action random allocation 2 - item:{0} original price:{1}".format(
                        str(bid_index), str(original_price)))

                    # Remove the node.
                    del sorted_bids[bid_index]

            self.logger.debug("execute Action random allocation 2")

            # Remove the bid if all their price elements were less than the reserved price.
            if len(bids_to_fulfill[index]) == 0:
                del bids_to_fulfill[index]

            self.logger.debug("execute Action random allocation 3")

        # Allocates randomly the available quantities
        for j in range(0, floor(qty_available)):

            prob = self.get_probability()
            index = floor(prob * len(bids_to_fulfill))
            if len(bids_to_fulfill) == 0:
                # All units have been assigned and there are no more bids.
                break
            else:

                # the unit is assigned to the first allocation proc for the bid.
                bids_to_fulfill[index][0].quantity = bids_to_fulfill[index][0].quantity - 1
                key = self.make_key(bids_to_fulfill[index][0].auction_key, bids_to_fulfill[index][0].bidding_object_key)

                # Create or update the allocation
                if key in allocations:
                    self.proc_module.increment_quantity_allocation(allocations[key], 1)
                else:
                    allocation = self.create_allocation(bids_to_fulfill[index][0].session_id,
                                                        bids_to_fulfill[index][0].auction_key, start,
                                                        stop, 1, reserved_price_low)
                    allocations[key] = allocation

                # Remove the node in case of no more units required.
                if bids_to_fulfill[index][0].quantity == 0:
                    bids = bids_to_fulfill[index]
                    del bids[0]

                    if len(bids_to_fulfill[index]) == 0:
                        del bids_to_fulfill[index]

        self.logger.debug("execute Action random allocation")
        return allocations

    def execute_auction(self, start: datetime, stop: datetime, bids_to_fulfill: DefaultDict[float, list],
                        qty_available: float, reserved_price: float) -> (dict, float):
        """

        :param self:
        :param start:
        :param stop:
        :param bids_to_fulfill:
        :param qty_available:
        :param reserved_price:
        :return:
        """
        sell_price = 0
        allocations = {}

        sorted_prices = sorted(bids_to_fulfill.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = bids_to_fulfill[price]

            if price < reserved_price:
                for i in range(0, len(alloc_temp)):
                    alloc_temp[i].quantity = 0
            else:
                for i in range(0, len(alloc_temp)):
                    if qty_available < alloc_temp[i].quantity:
                        alloc_temp[i].quantity = qty_available
                        if qty_available > 0:
                            sell_price = price
                            qty_available = 0
                    else:
                        qty_available = qty_available - alloc_temp[i].quantity
                        sell_price = price

        # There are more units available than requested
        if qty_available > 0:
            sell_price = reserved_price

        # Creates allocations
        sorted_prices = sorted(bids_to_fulfill.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp: List[AllocProc] = bids_to_fulfill[price]
            for i in range(0, len(alloc_temp)):
                key = self.make_key(alloc_temp[i].auction_key, alloc_temp[i].bidding_object_key)
                if key in allocations:
                    self.proc_module.increment_quantity_allocation(allocations[alloc_temp[i].bidding_object_key],
                                                                   alloc_temp[i].quantity)
                else:
                    allocation = self.create_allocation(alloc_temp[i].session_id,
                                                        alloc_temp[i].auction_key,
                                                        start, stop,
                                                        alloc_temp[i].quantity,
                                                        sell_price)

                    allocations[key] = allocation

        self.logger.debug("two auction module: after create allocations - # nbr created: {0}".format(len(allocations)))
        return allocations, sell_price

    def apply_mechanism(self, start: datetime, stop: datetime, allocations: Dict[str, BiddingObject],
                        price: float, q: float):
        """
        Apply mechanism
        :param self:
        :param start:
        :param stop:
        :param allocations:
        :param price:
        :param q:
        :return:
        """
        self.logger.debug("starting ApplyMechanism Q: {0}".format(q))

        for bidding_object_key in allocations:
            alloc = allocations[bidding_object_key]
            quantity = floor(self.proc_module.get_allocation_quantity(alloc))
            units_to_pass = 0.0
            for j in range(0, quantity):
                prob = self.get_probability()

                if prob <= q:  # pass a unit.
                    units_to_pass = units_to_pass + 1

            self.logger.debug("qty to pass: {0}".format(str(units_to_pass)))
            if units_to_pass > 0:
                if units_to_pass < quantity:
                    alloc2 = self.create_allocation(alloc.get_session(),
                                                    alloc.get_auction_key(),
                                                    start, stop,
                                                    units_to_pass,
                                                    price)

                    units_to_add = units_to_pass * -1
                    self.proc_module.increment_quantity_allocation(alloc, units_to_add)

                    allocations[self.make_key(alloc2.auction_key, alloc2.bidding_object_key)] = alloc2
                else:
                    self.proc_module.change_allocation_price(alloc, price)
        self.logger.debug("ending ApplyMechanism")

    def execute(self, request_params: Dict[str, FieldValue], auction_key: str,
                start: datetime, stop: datetime, bids: dict) -> list:
        """
        Executes the auction procedure for an specific auction.

        :param request_params: request params included
        :param auction_key: auction key identifying the auction
        :param start: start datetime
        :param stop: stop datetime
        :param bids: bidding objects included
        :return:
        """

        self.logger.debug("two auction generalized module: start execute {0}".format(len(bids)))

        bandwidth_to_sell_low = self.proc_module.get_param_value('bandwidth01', request_params)
        bandwidth_to_sell_high = self.proc_module.get_param_value('bandwidth02', request_params)

        reserve_price_low = self.proc_module.get_param_value('reserveprice01', request_params)
        reserve_price_high = self.proc_module.get_param_value('reserveprice02', request_params)

        bl = self.proc_module.get_param_value('maxvalue01', request_params)
        bh = self.proc_module.get_param_value('maxvalue02', request_params)

        tot_demand = self.proc_module.calculate_requested_quantities(bids)

        self.logger.debug("totalReq: {0} total units: {1}".format(str(tot_demand),
                                                                  str(bandwidth_to_sell_low + bandwidth_to_sell_high)))

        if tot_demand > (bandwidth_to_sell_low + bandwidth_to_sell_high):

            self.logger.debug("Splitting resources")
            bids_low, bids_high = self.proc_module.separate_bids(bids, bl)

            # Calculate the number of bids on both auctions.
            nl = self.proc_module.calculate_requested_quantities(bids_low)
            nh = self.proc_module.calculate_requested_quantities(bids_high)

            qStar = 0
            Q = 0.2

            self.logger.debug("Starting the execution of the mechanism")

            if nl > 0 and nh > 0:

                # Find the probability of changing from the high budget to low budget auction.
                TwoAuctionMechanismGeneralized * mechanism = new TwoAuctionMechanismGeneralized();
                a = 0.01
                b = 0.8

                mechanism->zeroin(nh, nl, bh, bl, bandwidth_to_sell_high,
                                  bandwidth_to_sell_low, reserve_price_high, reserve_price_low, Q, & a, & b);
                qStar = a

                while (qStar >= 0.25) and (Q <= 1.0):
                    Q = Q + 0.03
                    a = 0.01
                    b = 0.8

                    mechanism->zeroin(nh, nl, bh, bl, bandwidth_to_sell_high,
                                      bandwidth_to_sell_low, reserve_price_high, reserve_price_low, Q, & a, & b)

                    qStar = a

                    self.logger.debug("Q: {0} qStar: {1}".format(str(Q), str(qStar)))

            self.logger.debug("Finished the execution of the mechanism")

            # Create requests for both auctions, it pass the users from an auction to the other.
            low_auction_allocs, high_auction_allocs, nl, nh = self.create_request(bids_low, bids_high, qStar,
                                                                                  reserve_price_low)

            # Execute auctions.

            allocations_low = self.execute_auction_random_allocation(reserve_price_low, auction_key, start, stop,
                                                                     low_auction_allocs, bandwidth_to_sell_low)

            alloctions_high, reserve_price_high = self.execute_auction(start, stop, high_auction_allocs,
                                                                       bandwidth_to_sell_low, reserve_price_high)

            self.logger.debug("after executeAuction high budget users")

            if Q > 0:
                # change bids from the high budget to low budget auction.
                self.apply_mechanism(start, stop, alloctions_high, reserve_price_low, Q)

            # Convert from the map to the final returning vector
            allocation_res = []
            for allocation_key in allocations_low:
                allocation_res.append(allocations_low[allocation_key])

            for allocation_key in alloctions_high:
                allocation_res.append(alloctions_high[allocation_key])

        else:

            self.logger.debug("auctioning without splitting resources")

            # All bids get units and pay the reserved price of the L Auction
            bids_low = {}
            low_auction_allocs, high_auction_allocs, nl, nh = self.create_request(bids_low, bids, 0, reserve_price_low)
            allocations, reserve_price_low = self.execute_auction(start, stop, high_auction_allocs,
                                                                  bandwidth_to_sell_low)

            # Convert from the map to the final allocationDB result
            allocation_res = []
            for allocation_key in allocations:
                allocation_res.append(allocations[allocation_key])

        self.logger.debug("two auction generalized module: end execute")
        return allocation_res

    def execute_user(self, request_params: Dict[str, FieldValue], auctions: dict,
                     start: datetime, stop: datetime) -> list:
        """
        Executes the module for an agent

        :param request_params: request params included
        :param auctions: list of auction to create bids
        :param start: start datetime
        :param stop: stop datetime
        :return: list of bids created.
        """
        print('in execute_user')
        return []

    def reset(self):
        """
        restart the module
        :return:
        """
        print('in reset')

    def get_module_info(self, option: ModuleInformation) -> str:
        self.logger.debug("two auction generalized module: start getModuleInfo")

        if option == ModuleInformation.I_MODNAME:
            return "Two Auction Module"
        elif option == ModuleInformation.I_ID:
            return "TwoAuction"
        elif option == ModuleInformation.I_VERSION:
            return "0.1"
        elif option == ModuleInformation.I_CREATED:
            return "2015/12/01"
        elif option == ModuleInformation.I_MODIFIED:
            return "2015/12/01"
        elif option == ModuleInformation.I_BRIEF:
            return "Auction process for spliting in low and high budget users"
        elif option == ModuleInformation.I_VERBOSE:
            return "The auction calculates a probability q, so high budget users are priced as low budget users."
        elif option == ModuleInformation.I_HTMLDOCS:
            return "http://www.uniandes.edu.co/... "
        elif option == ModuleInformation.I_PARAMS:
            return "BANDWIDTH01(bandwidth low auction) BANDWIDTH02(bandwidth high auction) \
                    RESERVEDPRICE0 (reserved price low auction) RESERVEDPRICE1 (reserved price high auction) \
                    MAXVALUE0(discriminating price low auction) MAXVALUE1(discriminating price high auction)"
        elif option == ModuleInformation.I_RESULTS:
            return "The set of assigments"
        elif option == ModuleInformation.I_AUTHOR:
            return "Andres Marentes"
        elif option == ModuleInformation.I_AFFILI:
            return "Universidad de los Andes, Colombia"
        elif option == ModuleInformation.I_EMAIL:
            return "la.marentes455@uniandes.edu.co"
        elif option == ModuleInformation.I_HOMEPAGE:
            return "http://homepage"
        else:
            return ''
