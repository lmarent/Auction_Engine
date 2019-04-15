from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.config_param import ConfigParam
from foundation.bidding_object import BiddingObject
from foundation.parse_format import ParseFormats
from foundation.module import ModuleInformation

from utils.auction_utils import log

from proc_modules.proc_module import ProcModule
from proc_modules.proc_module import AllocProc

from math import ceil

from typing import List
from typing import Dict
from typing import DefaultDict
from datetime import datetime
from collections import defaultdict


class TwoAuctionPerfectInformation(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(TwoAuctionPerfectInformation, self).__init__(module_name, module_file, module_handle, config_group)
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

    def destroy_module(self):
        """
        method to be executed when destroying the class
        :return:
        """
        self.logger.debug('in destroy_module')

    def create_request(self, bids: Dict[str, BiddingObject]) -> (DefaultDict[float, list]):
        """
        Creates allocation requests for low and high auctions. It promotes some high auction bid into the
        low auction

        :param self:
        :param bids:    bids competing in the auction

        :return: allocations request in the auction.
        """
        self.logger.debug("create request bids {0}".format(str(len(bids))))

        # go through all high budget bids and pass some of their units as low auction requests.
        auction_allocs: DefaultDict[float, list] = defaultdict(list)
        for bidding_object_key in bids:
            bidding_object = bids[bidding_object_key]
            elements = bidding_object.elements
            for element_name in elements:
                config_params = elements[element_name]
                price = ParseFormats.parse_float(config_params["unitprice"].value)
                quantity = ParseFormats.parse_float(config_params["quantity"].value)

                alloc = AllocProc(bidding_object.get_parent_key(), bidding_object.get_key(),
                                  element_name, bidding_object.get_session(), quantity, price)

                auction_allocs[price].append(alloc)

        self.logger.debug("create requests after budget bids {0}".format(str(len(auction_allocs))))
        return auction_allocs

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
        self.logger.debug("bas module: start execute num bids:{0}".format(str(len(bids))))
        bandwidth_to_sell_low = self.proc_module.get_param_value('bandwidth01', request_params)
        bandwidth_to_sell_high = self.proc_module.get_param_value('bandwidth02', request_params)

        self.logger.debug('bandwidth_to_sell_low:{0} - bandwidth_to_sell_high:{1}'.format(str(bandwidth_to_sell_low),
                                                                                          str(bandwidth_to_sell_high)))

        reserve_price_low: float = self.proc_module.get_param_value('reserveprice01', request_params)
        reserve_price_high: float = self.proc_module.get_param_value('reserveprice02', request_params)

        self.logger.debug('reserve_price_low: {0} - reserve_price_high:{1}'.format(str(reserve_price_low),
                                                                                   str(reserve_price_high)))

        bl = self.proc_module.get_param_value('maxvalue01', request_params)

        bids_low, bids_high = self.proc_module.separate_bids(bids, bl)

        # Calculate the number of quantities requested on both auctions.
        nh = ceil(self.proc_module.calculate_requested_quantities(bids_high))

        tot_demand = self.proc_module.calculate_requested_quantities(bids)

        if (tot_demand > (bandwidth_to_sell_low + bandwidth_to_sell_high)) and (bandwidth_to_sell_high < nh):

            alloc_low = self.create_request(bids_low)
            allocations_low, sell_price_low = self.execute_auction(start, stop, alloc_low,
                                                                   bandwidth_to_sell_low, reserve_price_low)

            alloc_high = self.create_request(bids_high)
            allocations_high, sell_price_high = self.execute_auction(start, stop, alloc_high,
                                                                     bandwidth_to_sell_high, reserve_price_high)

            # Convert from the map to the final returning vector
            allocation_res = []
            for allocation_key in allocations_low:
                allocation_res.append(allocations_low[allocation_key])

            for allocation_key in allocations_high:
                allocation_res.append(allocations_high[allocation_key])

        else:

            allocs = self.create_request(bids)
            allocations, sell_price = self.execute_auction(start, stop, allocs,
                                                           bandwidth_to_sell_low + bandwidth_to_sell_high,
                                                           reserve_price_low)

            # Convert from the map to the final returning vector
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
            return "Two Auction Perfect Information Module"
        elif option == ModuleInformation.I_ID:
            return "TwoAuctionPerfectInformation"
        elif option == ModuleInformation.I_VERSION:
            return "0.1"
        elif option == ModuleInformation.I_CREATED:
            return "2015/12/01"
        elif option == ModuleInformation.I_MODIFIED:
            return "2015/12/01"
        elif option == ModuleInformation.I_BRIEF:
            return "Auction process for spliting in low and high budget users"
        elif option == ModuleInformation.I_VERBOSE:
            return "It assumes that users are splitted as low and high budget"
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
