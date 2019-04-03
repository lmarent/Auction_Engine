from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.parse_format import ParseFormats
from foundation.config_param import ConfigParam
from foundation.bidding_object import BiddingObject
from foundation.auction import AuctioningObjectType

from proc_modules.proc_module import ProcModule

from datetime import datetime
from utils.auction_utils import log
from typing import Dict
from proc_modules.proc_module import AllocProc
from collections import defaultdict


class BasicModule(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(BasicModule, self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}
        self.logger = log().get_logger()
        self.bandwidth = 0
        self.reserved_price = 0
        self.domain = 0
        self.proc_module = ProcModule()

    def init_module(self, config_param_list: Dict[str, ConfigParam]):
        self.logger.debug('in init_module')
        self.config_param_list = config_param_list
        self.domain = config_param_list['domainid']

    @staticmethod
    def make_key(auction_key: str, bid_key: str) -> str:
        return auction_key + '-' + bid_key

    def create_allocation(self, session_id: str, auction_key: str, start: datetime,
                          stop: datetime, quantity: float, price: float):

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

    def increment_quantity_allocation(self, allocation: BiddingObject, quantity: float):

        self.logger.debug("bas module: starting increment quantity allocation")
        elements = allocation.elements

        # there is only one element
        for element_name in elements:
            config_dict = elements[element_name]
            # remove the field for updating quantities
            field: ConfigParam = config_dict.pop('quantity')
            # Insert again the field.
            temp_qty = ParseFormats.parse_float(field.value)
            temp_qty += quantity
            fvalue = str(temp_qty)
            field.value = fvalue
            config_dict[field.name] = field

        raise ValueError("Field quantity was not included in the allocation")

    def calculate_requested_quantities(self, bidding_objects: Dict[str, BiddingObject]):

        self.logger.debug("bas module: starting calculateRequestedQuantities")
        sum_quantity = 0
        for bidding_object_key in bidding_objects:
            bidding_object = bidding_objects[bidding_object_key]
            elements = bidding_object.elements
            for element_name in elements:
                config_dict = elements[element_name]
                quantity = float(config_dict['quantity'].value)
                sum_quantity = sum_quantity + quantity

        self.logger.debug("bas module - ending calculateRequestedQuantities: {0}".format(sum_quantity))
        return sum_quantity

    @staticmethod
    def get_bid_price(bidding_object: BiddingObject):
        unit_price = -1

        elements = bidding_object.elements
        for element_name in elements:
            config_dict = elements[element_name]
            unit_price = float(config_dict['unitprice'].value)
            break
        return unit_price

    def separate_bids(self, bidding_objects: Dict[str, BiddingObject], bl: float) -> (Dict[str, BiddingObject],
                                                                                      Dict[str, BiddingObject]):
        """

        :param bidding_objects:
        :param bl:
        :return:
        """
        self.logger.debug("bas module: Starting separateBids")
        bids_high = {}
        bids_low = {}
        for bidding_object_key in bidding_objects:
            bidding_object = bidding_objects[bidding_object_key]
            price = self.get_bid_price(bidding_object)
            if price >= 0:
                if price > bl:
                    bids_high[bidding_object_key] = bidding_object
                else:
                    bids_low[bidding_object_key] = bidding_object

        self.logger.debug("bas module: Ending separateBids")
        return bids_low, bids_high

    def destroy_module(self):
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

        tot_demand = self.calculate_requested_quantities(bids)
        bandwidth_to_sell = self.proc_module.get_param_value('bandwidth', request_params)
        reserve_price = self.proc_module.get_param_value('reserveprice', request_params)

        # Order bids classifying them by whether they compete on the low and high auction.
        bids_low_rct, bids_high_rct = self.separate_bids(bids, 0.5)

        # Calculate the number of bids on both auctions.
        nl = self.calculate_requested_quantities(bids_low_rct)
        nh = self.calculate_requested_quantities(bids_high_rct)

        ordered_bids = defaultdict(list)
        for bidding_object_key in bids:
            bidding_object = bids[bidding_object_key]
            elements = bidding_object.elements
            for element_name in elements:
                config_params = elements[element_name]
                price = ParseFormats.parse_float(config_params["unitprice"].value)
                quantity = ParseFormats.parse_float(config_params["quantity"].value)
                alloc = AllocProc(bidding_object.get_auction_key(), bidding_object.get_key(),
                                  element_name, bidding_object.get_session(), quantity)
                ordered_bids[price].append(alloc)

        qty_available = bandwidth_to_sell
        sell_price = 0

        self.logger.debug("bas module - qty available:{0}".format(qty_available))

        sorted_prices = sorted(ordered_bids.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = sorted_prices[price]

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

        self.logger.debug("bas module: after executing the auction")

        allocations = {}

        # Creates allocations
        sorted_prices = sorted(ordered_bids.keys(), reverse=True)
        for price in sorted_prices:
            alloc_temp = sorted_prices[price]
            for i in range(0, len(alloc_temp)):
                if self.make_key(alloc_temp[i].auction_key, alloc_temp[i].bidding_object_key) in allocations:
                    self.increment_quantity_allocation(allocations[alloc_temp[i].bidding_object_key],
                                                       alloc_temp[i].quantity)
                else:
                    allocation = self.create_allocation(alloc_temp[i].session_id,
                                                        alloc_temp[i].auction_key,
                                                        start, stop,
                                                        alloc_temp[i].quantity,
                                                        sell_price)

                    allocations[self.make_key(alloc_temp[i].auction_key, alloc_temp[i].bidding_object_key)] = allocation

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
        print('in execute_user')
        return []

    def reset(self):
        print('in reset')
