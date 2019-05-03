from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.module import ModuleInformation

from proc_modules.proc_module import ProcModule

from utils.auction_utils import log
from typing import Dict
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

    def calculate_allocation_quantities(self, start: datetime, stop: datatime, tot_quantity: float,
                                        ordered_bids: DefaultDict[float, list]) \
            -> Dict[str, float]:
        """
        Calculates the allocation quantity to sell at each price bid. In the paper this corresponds to min(q_i, Q_i (p_i, s_{-i}))

        :param tot_quantity: available total quantity to sell. In the paper, it corresponds to Q
        :param ordered_bids: list of bids for which we want to calculate the maximum available quantity.
        :return: return a dictionay with the id of the bid and its corresponding maximum  available quantity.
        """
        qty_acum = 0
        allocations = {}

        sorted_prices = sorted(ordered_bids.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = ordered_bids[price]

            acum_price = 0
            for i in range(0, len(alloc_temp)):
                acum_price += alloc_temp[i].quantity

            for i in range(0, len(alloc_temp)):
                alloc_qty = min(alloc_temp[i].quantity,
                                ceil(tot_quantity - qty_acum - acum_price + alloc_temp[i].quantity))

                key = self.proc_module.make_key(alloc_temp[i].auction_key, alloc_temp[i].bidding_object_key)
                allocation = self.proc_module.create_allocation(self.domain, alloc_temp[i].session_id,
                                                                alloc_temp[i].bidding_object_key,
                                                                start, stop,
                                                                alloc_qty,
                                                                0)
                allocations[key] = allocation
            qty_acum = qty_acum + acum_price

        return allocations


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

        # get the maximum available quantities for bids.
        maximum_available_quantities = self.calculate_maximum_available_quantities(ordered_bids)

        #

