from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.config_param import ConfigParam
from foundation.bidding_object import BiddingObject
from foundation.auction import AuctioningObjectType
from foundation.module import ModuleInformation
from foundation.parse_format import ParseFormats

from proc_modules.proc_module import ProcModule
from proc_modules.proc_module import AllocProc
from proc_modules.two_auction_mechanism_generalized import TwoAuctionMechanismGeneralized

from math import floor
from math import ceil
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

    def init_module(self, config_params: Dict[str, FieldValue]):
        """
        Initializes the module

        :param config_params: dictionary with the given configuration parameters
        """
        self.logger.debug('in init_module')
        self.config_params = config_params
        self.domain = self.proc_module.get_param_value('domainid', config_params)


    def destroy_module(self):
        """
        method to be executed when destroying the class
        :return:
        """
        self.logger.debug('in destroy_module')

    @staticmethod
    def get_probability() -> float:
        """
        Gets a uniform distribution sample for checking if a request should be promoted to
        the low auction

        :return:
        """
        return random.uniform(0, 1)

    def create_request(self, bids_low: Dict[str, BiddingObject], bids_high: Dict[str, BiddingObject],
                       q_star: float) -> (DefaultDict[int, list], DefaultDict[float, list], int, int):
        """
        Creates allocation requests for low and high auctions. It promotes some high auction bid into the
        low auction

        :param self:
        :param bids_low:    bids competing in the low auction
        :param bids_high:   bids competing in the high auction
        :param q_star:      probability of being promoted.

        :return: allocations request in the low and high auctions.
        """
        self.logger.debug(
            "create requests Nbr low bids {0} - Nbr high bids {1}".format(str(len(bids_low)), str(len(bids_high))))

        nhtmp = 0
        nltmp = 0

        # creates the request for the L auction.
        index = 0
        low_auction_allocs: DefaultDict[int, list] = defaultdict(list)
        for bidding_object_key in bids_low:
            bidding_object = bids_low[bidding_object_key]
            elements = bidding_object.elements
            inserted = False
            for element_name in elements:
                config_params = elements[element_name]
                price = ParseFormats.parse_float(config_params["unitprice"].value)
                quantity = ParseFormats.parse_float(config_params["quantity"].value)

                if quantity > 0:
                    alloc = AllocProc(bidding_object.get_parent_key(), bidding_object.get_key(),
                                      element_name, bidding_object.get_session(), quantity, price)
                    low_auction_allocs[index].append(alloc)
                    nltmp = nltmp + quantity
                    inserted = True

            # Only increase index if there was another node inserted.
            if inserted:
                index = index + 1

        self.logger.debug("create requests after low budget bids {0}".format(str(len(low_auction_allocs))))

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
                alloc1 = AllocProc(bidding_object.get_parent_key(), bidding_object.get_key(),
                                   element_name, bidding_object.get_session(), quantity, price)

                high_auction_allocs[price].append(alloc1)
                nhtmp = nhtmp + quantity - units_to_pass

                if units_to_pass > 0:
                    # quantities in the L auction.
                    alloc2 = AllocProc(bidding_object.get_parent_key(), bidding_object.get_key(),
                                       element_name, bidding_object.get_session(), units_to_pass, price)
                    alloc_bids.append(alloc2)
                    inserted = True

                self.logger.debug("bid set: {0} units pass: {1}".format(bidding_object.get_key(), str(units_to_pass)))
                nltmp = nltmp + units_to_pass

            # Only increase index if there was another node inserted.
            if inserted:
                low_auction_allocs[index].extend(alloc_bids)
                index = index + 1

        nl = nltmp
        nh = nhtmp

        self.logger.debug(
            "ending create requests low_auction request {0} nl: {1}-high auction request {2} nh: {3}".format(
                str(len(low_auction_allocs)), str(nl), str(len(high_auction_allocs)), str(nh)))
        return low_auction_allocs, high_auction_allocs, nl, nh

    def execute_auction(self, start: datetime, stop: datetime, bids_to_fulfill: DefaultDict[float, list],
                        qty_available: float, reserved_price: float) -> (dict, float):
        """
        Executes a second price auction for high budget users.

        :param start: datetime when the allocation will start
        :param stop:  datetime when the allocation will stop
        :param bids_to_fulfill: allocation requests to be allocated
        :param qty_available:   quantity available to allocations
        :param reserved_price:  minimum price for selling and to be used in the allocation.
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
                key = self.proc_module.make_key(alloc_temp[i].auction_key, alloc_temp[i].bidding_object_key)
                if key in allocations:
                    self.proc_module.increment_quantity_allocation(allocations[alloc_temp[i].bidding_object_key],
                                                                   alloc_temp[i].quantity)
                else:
                    allocation = self.proc_module.create_allocation(self.domain,
                                                                    alloc_temp[i].session_id,
                                                                    alloc_temp[i].bidding_object_key,
                                                                    start, stop,
                                                                    alloc_temp[i].quantity,
                                                                    sell_price)

                    allocations[key] = allocation

        self.logger.debug("two auction module: after create allocations - # nbr created: {0}".format(len(allocations)))
        return allocations, sell_price

    def execute_auction_random_allocation(self, start: datetime, stop: datetime,
                                          bids_to_fulfill: DefaultDict[int, list],
                                          qty_available: float, reserved_price: float) -> dict:
        """
        Creates allocations according with a random allocation.

        :param start:              datetime when the allocation will start
        :param stop:               datetime when the allocation will stop
        :param bids_to_fulfill:    allocation requests to be allocated
        :param qty_available:      quantity available to allocations
        :param reserved_price:     minimum price for selling and to be used in the allocation.

        :return: dictionary with created allocations
        """
        self.logger.debug("execute Action random allocation")

        allocations = {}

        # Create allocations with zero quantity for all bids.
        sorted_indexes: List[int] = sorted(bids_to_fulfill.keys(), reverse=True)
        for index in sorted_indexes:
            self.logger.debug("execute action random allocation 1")
            sorted_bids = bids_to_fulfill[index]
            for bid_index in range(len(sorted_bids) - 1, -1, -1):
                alloc_proc = sorted_bids[bid_index]
                key = self.proc_module.make_key(alloc_proc.auction_key, alloc_proc.bidding_object_key)
                if key not in allocations:
                    allocation = self.proc_module.create_allocation(self.domain,
                                                                        alloc_proc.session_id,
                                                                        alloc_proc.bidding_object_key,
                                                                        start,
                                                                        stop, 0, reserved_price)

                    allocations[key] = allocation

                # Remove the node if their price is less than the reserve price.
                if alloc_proc.original_price < reserved_price:
                    del sorted_bids[bid_index]

            self.logger.debug("execute Action random allocation 2")

            # Remove the bid if all their price elements were less than the reserved price.

            if len(bids_to_fulfill[index]) == 0:
                del bids_to_fulfill[index]

            self.logger.debug("execute Action random allocation 3")

        self.logger.info("nbr allocation so far: {0}".format(str(len(allocations))))
        self.logger.info("qty available: {0}".format(str(ceil(qty_available))))
        # Allocates randomly the available quantities
        indexes = list(bids_to_fulfill.keys())
        for j in range(0, ceil(qty_available)):

            prob = self.get_probability()
            length = len(indexes)
            main_index = floor(prob * length)
            if len(indexes) == 0:
                # All units have been assigned and there are no more bids.
                break
            else:
                index = indexes[main_index]
                # the unit is assigned to the first allocation proc for the bid.
                bids_to_fulfill[index][0].quantity = bids_to_fulfill[index][0].quantity - 1
                key = self.proc_module.make_key(bids_to_fulfill[index][0].auction_key,
                                                bids_to_fulfill[index][0].bidding_object_key)

                # Create or update the allocation
                if key in allocations:
                    self.proc_module.increment_quantity_allocation(allocations[key], 1)
                else:
                    allocation = self.proc_module.create_allocation(self.domain,
                                                                    bids_to_fulfill[index][0].session_id,
                                                                    bids_to_fulfill[index][0].bidding_object_key,
                                                                    start,
                                                                    stop, 1, reserved_price)
                    allocations[key] = allocation

                # Remove the node in case of no more units required.
                if bids_to_fulfill[index][0].quantity == 0:
                    bids = bids_to_fulfill[index]
                    del bids[0]

                    if len(bids_to_fulfill[index]) == 0:
                        del bids_to_fulfill[index]
                        del indexes[main_index]

        self.logger.debug("execute Action random allocation")
        return allocations

    def apply_mechanism(self, start: datetime, stop: datetime, allocations: Dict[str, BiddingObject],
                        reserved_price: float, q: float):
        """
        Apply the two auction mechanism for a set of bidding objects.

        :param start: datetime when the allocation will start
        :param stop:  datetime when the allocation will stop
        :param allocations:  allocation request to allocate
        :param reserved_price: reserved price to be used for applying the mechanism.
        :param q:     probability of promoting a user competing in the high budget auction.
        :return:
        """
        self.logger.debug("starting ApplyMechanism Q: {0}".format(q))
        allocations2 = {}

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
                    alloc2 = self.proc_module.create_allocation(self.domain,
                                                                alloc.get_session(),
                                                                alloc.get_parent_key(),
                                                                start, stop,
                                                                units_to_pass,
                                                                reserved_price)

                    units_to_add = units_to_pass * -1
                    self.proc_module.increment_quantity_allocation(alloc, units_to_add)

                    allocations2[self.proc_module.make_key(alloc2.get_parent_key(), alloc2.get_key())] = alloc2
                else:
                    self.proc_module.change_allocation_price(alloc, reserved_price)

        # Inserts new allocations in allocation dictionary.
        for key in allocations2:
            alloc = allocations2[key]
            allocations[key] = alloc
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

        self.logger.info("two auction generalized module: start execute {0}".format(len(bids)))

        bandwidth_to_sell_low = self.proc_module.get_param_value('bandwidth01', request_params)
        bandwidth_to_sell_high = self.proc_module.get_param_value('bandwidth02', request_params)

        self.logger.info('bandwidth_to_sell_low:{0} - bandwidth_to_sell_high:{1}'.format(str(bandwidth_to_sell_low),
                                                                                         str(bandwidth_to_sell_high)))

        reserve_price_low: float = self.proc_module.get_param_value('reserveprice01', request_params)
        reserve_price_high: float = self.proc_module.get_param_value('reserveprice02', request_params)

        self.logger.info('reserve_price_low: {0} - reserve_price_high:{1}'.format(str(reserve_price_low),
                                                                                  str(reserve_price_high)))

        bl = self.proc_module.get_param_value('maxvalue01', request_params)
        bh = self.proc_module.get_param_value('maxvalue02', request_params)

        tot_demand = self.proc_module.calculate_requested_quantities(bids)

        self.logger.info("totalReq: {0} total units: {1}".format(str(tot_demand),
                                                                 str(bandwidth_to_sell_low + bandwidth_to_sell_high)))

        if tot_demand > (bandwidth_to_sell_low + bandwidth_to_sell_high):

            self.logger.info("Splitting resources")
            bids_low, bids_high = self.proc_module.separate_bids(bids, bl)

            # Calculate the number of quantities requested on both auctions.
            nl = ceil(self.proc_module.calculate_requested_quantities(bids_low))
            nh = ceil(self.proc_module.calculate_requested_quantities(bids_high))

            if nh < bandwidth_to_sell_high:
                bandwidth_to_sell_low = bandwidth_to_sell_low + (bandwidth_to_sell_high - nh)
                bandwidth_to_sell_high = nh

            if nl < bandwidth_to_sell_low:
                bandwidth_to_sell_high = bandwidth_to_sell_high + (bandwidth_to_sell_low - nl)
                bandwidth_to_sell_low = nl

            self.logger.info("Number of quantities requested low:{0} high:{1}".format(str(nl), str(nh)))

            q_star = 0
            q = 0.2

            self.logger.info("Starting the execution of the mechanism")

            if nl > 0 and nh > 0:

                # Find the probability of changing from the high budget to low budget auction.
                mechanism = TwoAuctionMechanismGeneralized()
                a = 0.01
                b = 0.8

                message = "nh:{0} nl:{1} bh:{2} bl:{3} bandwidth_to_sell_high:{4}".format(str(nh), str(nl),
                                                                                          str(bh), str(bl),
                                                                                          str(bandwidth_to_sell_high))
                message = message + " bandwidth_to_sell_low:{0} reserve_price_high:{1} reserve_price_low:{2}".format(
                    str(bandwidth_to_sell_low), str(reserve_price_high), str(reserve_price_low))

                message = message + " q:{0} a:{1} b:{2}".format(str(q), str(a), str(b))
                self.logger.info(message)

                res, a, b = mechanism.zero_in(nh, nl, bh, bl, bandwidth_to_sell_high,
                                              bandwidth_to_sell_low, reserve_price_high, reserve_price_low, q, a, b)
                q_star = a

                while (q_star >= 0.25) and (q <= 1.0):
                    q = q + 0.03
                    a = 0.01
                    b = 0.8

                    message = "nh:{0} nl:{1} bh:{2} bl:{3} bandwidth_to_sell_high:{4}".format(str(nh), str(nl),
                                                                                              str(bh), str(bl),
                                                                                              str(
                                                                                                  bandwidth_to_sell_high))
                    message = message + " bandwidth_to_sell_low:{0} reserve_price_high:{1} reserve_price_low:{2}".format(
                        str(bandwidth_to_sell_low), str(reserve_price_high), str(reserve_price_low))

                    message = message + " q:{0} a:{1} b:{2}".format(str(q), str(a), str(b))
                    self.logger.info(message)

                    res, a, b = mechanism.zero_in(nh, nl, bh, bl, bandwidth_to_sell_high,
                                                  bandwidth_to_sell_low, reserve_price_high, reserve_price_low, q, a, b)

                    q_star = a

                    self.logger.info("Q: {0} qStar: {1}".format(str(q), str(q_star)))

            self.logger.info("Finished the execution of the mechanism q_start {0}".format(str(q_star)))

            self.logger.info("bids_low {0} - bids_high {1}".format(len(bids_low), len(bids_high)))

            # Create requests for both auctions, it passes the users from an auction to the other.
            low_auction_allocs, high_auction_allocs, nl, nh = self.create_request(bids_low, bids_high, q_star)

            self.logger.info("low auctions_allocs {0} - high_auction_allocs {1}".format(len(low_auction_allocs),
                                                                                        len(high_auction_allocs)))
            # Execute auctions.

            allocations_low = self.execute_auction_random_allocation(start, stop, low_auction_allocs,
                                                                     bandwidth_to_sell_low, reserve_price_low)

            allocations_high, reserve_price_high = self.execute_auction(start, stop, high_auction_allocs,
                                                                        bandwidth_to_sell_high, reserve_price_high)

            # code to debug.
            sell_prices_high = []
            qty_allocates_high = []
            for key in allocations_high:
                allocation = allocations_high[key]
                qty = self.proc_module.get_allocation_quantity(allocation)
                sell_price = self.proc_module.get_bid_price(allocation)
                sell_prices_high.append(sell_price)
                qty_allocates_high.append(qty)

            self.logger.info('sell prices high: {0}'.format(str(sell_prices_high)))
            self.logger.info('qty allocates high: {0}'.format(str(qty_allocates_high)))

            sell_prices_low = []
            qty_allocates_low = []
            for key in allocations_low:
                allocation = allocations_low[key]
                qty = self.proc_module.get_allocation_quantity(allocation)
                sell_price = self.proc_module.get_bid_price(allocation)
                sell_prices_low.append(sell_price)
                qty_allocates_low.append(qty)

            self.logger.info('sell prices low: {0}'.format(str(sell_prices_low)))
            self.logger.info('qty allocates low {0}:'.format(str(qty_allocates_low)))

            self.logger.info(
                "after executeAuction high budget users nbr allocations: {0}".format(len(allocations_high)))

            if q > 0:
                # change bids from the high budget to low budget auction.
                self.apply_mechanism(start, stop, allocations_high, reserve_price_low, q)

            # Convert from the map to the final returning vector
            allocation_res = []
            for allocation_key in allocations_low:
                allocation = allocations_low[allocation_key]
                allocation_res.append(allocation)
                self.logger.info(
                    "allocation low key: {0} - bidding object {1}".format(allocation_key, allocation.get_parent_key()))

            for allocation_key in allocations_high:
                allocation = allocations_high[allocation_key]
                allocation_res.append(allocation)
                self.logger.info(
                    "allocation high key: {0} - bidding object {1}".format(allocation_key, allocation.get_parent_key()))

        else:

            self.logger.info("auctioning without splitting resources")

            # All bids get units and pay the reserved price of the L Auction
            bids_low = {}
            low_auction_allocs, high_auction_allocs, nl, nh = self.create_request(bids_low, bids, 0)

            allocations, reserve_price_low = self.execute_auction(start, stop, high_auction_allocs,
                                                                  bandwidth_to_sell_low + bandwidth_to_sell_high,
                                                                  reserve_price_low)

            # Convert from the map to the final allocationDB result
            allocation_res = []
            for allocation_key in allocations:
                allocation = allocations[allocation_key]
                allocation_res.append(allocation)
                self.logger.info(
                    "allocation key: {0} - bidding object {1}".format(allocation_key, allocation.get_parent_key()))

        self.logger.info("two auction generalized module: end execute")
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
        return []

    def reset(self):
        """
        restart the module
        :return:
        """
        print('in reset')

    def get_module_info(self, option: ModuleInformation) -> str:
        """
        Gets module information for who is implementing the mechanism.

        :param option: option (type of information) to be reported.
        :return: string with the information
        """
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
