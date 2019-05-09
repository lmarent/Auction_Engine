from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.module import ModuleInformation

from proc_modules.proc_module import ProcModule
from proc_modules.proc_module import AllocProc

from utils.auction_utils import log
from typing import Dict
from typing import DefaultDict
from datetime import datetime
from math import ceil


class ProgressiveSecondPrice(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(ProgressiveSecondPrice, self).__init__(module_name, module_file, module_handle, config_group)
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
        pass

    @staticmethod
    def calculate_allocation_quantities(tot_quantity: float, ordered_bids: DefaultDict[float, list],
                                        bid_to_exclude: str = None) -> Dict[str, AllocProc]:
        """
        Calculates the allocation quantity to sell at each price bid.

        In the paper this corresponds to min(q_i, Q_i (p_i, s_{-i}))

        :param tot_quantity: available total quantity to sell. In the paper, it corresponds to Q
        :param ordered_bids: list of bids for which we want to calculate the maximum available quantity.
        :param bid_to_exclude: in case of giving this is a bid that should be excluded form the calculation.
        :return: return a dictionay with the id of the bid and its corresponding maximum  available quantity.
        """
        qty_acum = 0
        allocations = {}

        sorted_prices = sorted(ordered_bids.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = ordered_bids[price]

            acum_price = 0
            for i in range(0, len(alloc_temp)):
                if alloc_temp[i].bidding_object_key != bid_to_exclude:
                    acum_price += alloc_temp[i].quantity

            for i in range(0, len(alloc_temp)):
                if alloc_temp[i].bidding_object_key != bid_to_exclude:
                    if tot_quantity - qty_acum - acum_price + alloc_temp[i].quantity > 0:
                        alloc_qty = min(alloc_temp[i].quantity,
                                        tot_quantity - qty_acum - acum_price + alloc_temp[i].quantity)
                    else:
                        alloc_qty = 0

                    alloc_proc = AllocProc(alloc_temp[i].auction_key, alloc_temp[i].bidding_object_key,
                                           alloc_temp[i].element_name, alloc_temp[i].session_id, alloc_qty,
                                           alloc_temp[i].original_price)

                    allocations[alloc_temp[i].bidding_object_key] = alloc_proc
            qty_acum = qty_acum + acum_price

        return allocations

    def calculate_allocations(self, tot_quantity: float, ordered_bids: DefaultDict[float, list])-> Dict[str, AllocProc]:
        """
        Calculates the allocation cost to sell for each bid. In the paper this corresponds to c_i(s)

        :param tot_quantity: available total quantity to sell. In the paper, it corresponds to Q
        :param ordered_bids: list of bids for which we want to calculate the maximum available quantity.
        :return:
        """
        allocations_all_bids = self.calculate_allocation_quantities(tot_quantity, ordered_bids)

        sorted_prices = sorted(ordered_bids.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = ordered_bids[price]

            for i in range(0, len(alloc_temp)):
                allocations_partial_bids = self.calculate_allocation_quantities(tot_quantity,
                                                                                ordered_bids,
                                                                                alloc_temp[i].bidding_object_key)
                bid_cost = 0
                for bid_key in allocations_partial_bids:
                    price = allocations_partial_bids[bid_key].original_price
                    alloc_qty = allocations_partial_bids[bid_key].quantity

                    alloc_qty_included = allocations_all_bids[bid_key].quantity
                    bid_cost = bid_cost + (price * (alloc_qty - alloc_qty_included))

                allocations_all_bids[alloc_temp[i].bidding_object_key].original_price = bid_cost

        return allocations_all_bids

    def create_allocations(self, start: datetime, stop: datetime, allocations: Dict[str, AllocProc]) -> list:
        """
        Create allocations based the dictionary of alloca procs created.

        :param start: when the allocation will start
        :param stop: when the allocation will end
        :param allocations: dictionary with alloc procs created
        :return: list fo a allocations to return
        """
        list_allocs = []
        for bid_key in allocations:
            alloc_proc = allocations[bid_key]
            if alloc_proc.quantity == 0:
                allocation = self.proc_module.create_allocation(self.domain, alloc_proc.session_id,
                                                            alloc_proc.bidding_object_key,
                                                            start, stop, alloc_proc.quantity,
                                                            0)
            else:
                allocation = self.proc_module.create_allocation(self.domain, alloc_proc.session_id,
                                                            alloc_proc.bidding_object_key,
                                                            start, stop, alloc_proc.quantity,
                                                            alloc_proc.original_price / alloc_proc.quantity)
            list_allocs.append(allocation)

        return list_allocs

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
        self.logger.debug("progressive second price auction: start execute num bids:{0}".format(str(len(bids))))

        bandwidth_to_sell = self.proc_module.get_param_value('bandwidth', request_params)

        # sort bids from upper to lower values
        ordered_bids = self.proc_module.sort_bids_by_price(bids)

        # get allocations from the mechanism
        allocations = self.calculate_allocations(bandwidth_to_sell, ordered_bids)

        # create the final list of allocations and return it
        return self.create_allocations(start, stop, allocations)

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
        self.logger.debug("Progressive second price: start getModuleInfo")

        if option == ModuleInformation.I_MODNAME:
            return "Progressive Second price procedure"
        elif option == ModuleInformation.I_ID:
            return "psp"
        elif option == ModuleInformation.I_VERSION:
            return "0.1"
        elif option == ModuleInformation.I_CREATED:
            return "2019/05/09"
        elif option == ModuleInformation.I_MODIFIED:
            return "2019/05/09"
        elif option == ModuleInformation.I_BRIEF:
            return "Auction process that put the cost of the bid equals to the compensation principle"
        elif option == ModuleInformation.I_VERBOSE:
            return "The auction process cost bids according to the willingness to pay of other users for \
                    the units being allocated"
        elif option == ModuleInformation.I_HTMLDOCS:
            return "http://www.uniandes.edu.co/... "
        elif option == ModuleInformation.I_PARAMS:
            return "BANDWIDTH (how much capacity is being auctioned)"
        elif option == ModuleInformation.I_RESULTS:
            return "The set of assigments"
        elif option == ModuleInformation.I_AUTHOR:
            return "Andres Marentes"
        elif option == ModuleInformation.I_AFFILI:
            return "Advicetec Ltda, Colombia"
        elif option == ModuleInformation.I_EMAIL:
            return "lamarentes455@gmail.com"
        elif option == ModuleInformation.I_HOMEPAGE:
            return "http://homepage"
        else:
            return ''
