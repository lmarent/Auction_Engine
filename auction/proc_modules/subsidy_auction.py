from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.module import ModuleInformation

from proc_modules.proc_module import ProcModule

from utils.auction_utils import log
from typing import Dict
from datetime import datetime


class SubsidyAuction(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(SubsidyAuction, self).__init__(module_name, module_file, module_handle, config_group)
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
        print('in destroy_module')

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

        bandwidth_to_sell = self.proc_module.get_param_value('bandwidth', request_params)
        reserve_price = self.proc_module.get_param_value('reserveprice', request_params)
        subsidy = self.proc_module.get_param_value('subsidy', request_params)
        discriminatory_price = self.proc_module.get_param_value('maxvalue01', request_params)

        tot_demand = self.proc_module.calculate_requested_quantities(bids)

        # Order bids classifying them by whether they compete on the low and high auction.
        bids_low_rct, bids_high_rct = self.proc_module.separate_bids(bids, 0.5)

        # Calculate the number of quantities on both auctions.
        nl = self.proc_module.calculate_requested_quantities(bids_low_rct)
        nh = self.proc_module.calculate_requested_quantities(bids_high_rct)

        ordered_bids = self.proc_module.sort_bids_by_price(bids, discriminatory_price, subsidy)

        qty_available = bandwidth_to_sell
        sell_price = 0

        self.logger.debug("subsidy auction module- qty available: {0}".format(qty_available))

        sorted_prices = sorted(ordered_bids.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = ordered_bids[price]

            if price < reserve_price:
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
            sell_price = reserve_price

        self.logger.debug("subsidy auction module: after executing the auction for bids")

        allocations = {}

        # Creates allocations
        sorted_prices = sorted(ordered_bids.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = ordered_bids[price]
            for i in range(0, len(alloc_temp)):
                key = self.proc_module.make_key(alloc_temp[i].auction_key, alloc_temp[i].bidding_object_key)
                if key in allocations:
                    self.proc_module.increment_quantity_allocation(allocations[alloc_temp[i].bidding_object_key],
                                                                   alloc_temp[i].quantity)
                else:
                    if alloc_temp[i].original_price < sell_price and alloc_temp[i].quantity > 0:
                        set_price = alloc_temp[i].original_price
                    else:
                        set_price = sell_price

                    allocation = self.proc_module.create_allocation(self.domain, alloc_temp[i].session_id,
                                                        alloc_temp[i].bidding_object_key,
                                                        start, stop,
                                                        alloc_temp[i].quantity,
                                                        set_price)
                    allocations[key] = allocation

        # Convert from the map to the final allocationDB result
        allocation_res = []
        for allocation_key in allocations:
            allocation_res.append(allocations[allocation_key])

        # Write a log with data of the auction
        self.logger.debug("starttime: {0} endtime:{1}".format(str(start), str(stop)))
        self.logger.debug("demand: {0} - demand low: {1} demand high {2}".format(str(tot_demand), str(nl), str(nh)))
        self.logger.debug("qty_sell: {0}".format(str(bandwidth_to_sell - qty_available)))
        self.logger.debug("reservedPrice:{0} sell price:{1}".format(str(reserve_price), str(sell_price)))

        self.logger.debug("bas module: end execute")

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
        self.logger.debug("subsidy auction module: start getModuleInfo")

        if option == ModuleInformation.I_MODNAME:
            return "Subsidy Auction procedure"
        elif option == ModuleInformation.I_ID:
            return "bas"
        elif option == ModuleInformation.I_VERSION:
            return "0.1"
        elif option == ModuleInformation.I_CREATED:
            return "2015/12/30"
        elif option == ModuleInformation.I_MODIFIED:
            return "2015/12/30"
        elif option == ModuleInformation.I_BRIEF:
            return "Auction process that give to a target group a % additional bid value"
        elif option == ModuleInformation.I_VERBOSE:
            return "The auction process gives cares about capacity"
        elif option == ModuleInformation.I_HTMLDOCS:
            return "http://www.uniandes.edu.co/... "
        elif option == ModuleInformation.I_PARAMS:
            return "BANDWIDTH SUBSIDY MAXVALUE0 (discriminating Bid)"
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
