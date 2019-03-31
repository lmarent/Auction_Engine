from foundation.module import Module
from foundation.auction import Auction
from foundation.auction import AuctioningObjectType
from foundation.bidding_object import BiddingObject
from foundation.field_value import FieldValue

from proc_modules.proc_module import ProcModule

from datetime import datetime
from typing import Dict
from utils.auction_utils import log


class BasicModuleUser(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(BasicModuleUser, self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}
        self.proc_module = ProcModule()
        self.domain = 0
        self.logger = log().get_logger()

    def init_module(self, config_params: dict):
        self.config_param_list = config_params
        self.domain = config_params['domainid']

    def check_parameters(self, request_params):
        required_fields = set()
        required_fields.add(self.proc_module.field_def_manager.get_field("quantity"))
        required_fields.add(self.proc_module.field_def_manager.get_field("totalbudget"))
        required_fields.add(self.proc_module.field_def_manager.get_field("maxvalue"))

        for field in required_fields:
            if field['key'] not in request_params:
                raise ValueError("basic module: ending check - it does not pass the check, \
                                 field not included {0}".format(field['key']))

    def create_bidding_object(self, auction_key: str, quantity: float, unit_budget: float,
                              unit_price: float, start: datetime, stop: datetime) -> BiddingObject:

        self.logger.debug("starting create bidding object")
        if unit_budget < unit_price:
            unit_price = unit_budget

        # build the elements of the bidding object
        elements = dict()
        config_elements = dict()
        record_id = "record_1"
        self.proc_module.insert_string_field("recordid", record_id, config_elements)
        self.proc_module.insert_float_field("quantity", quantity, config_elements)
        self.proc_module.insert_double_field("unitprice", unit_price, config_elements)
        elements[record_id] = config_elements

        # build the options (time intervals)
        options = dict()
        option_id = 'option_1'
        config_options = dict()
        self.proc_module.insert_datetime_field("start", start, config_options)
        self.proc_module.insert_datetime_field("stop", stop, config_options)
        options[option_id] = config_options

        bidding_object_id = self.proc_module.get_bidding_object_id()
        bidding_object_key = str(self.domain) + '.' + bidding_object_id
        bidding_object = BiddingObject(auction_key, bidding_object_key,
                                       AuctioningObjectType.BID, elements, options)

        self.logger.debug("ending create bidding object")
        return bidding_object

    def destroy_module(self):
        pass

    def execute(self, auction_key: str, start: datetime, stop: datetime, bids: dict) -> dict:
        return {}

    def execute_user(self, request_params: Dict[str, FieldValue], auctions: dict,
                     start: datetime, stop: datetime) -> list:
        self.logger.debug("starting execute user")
        try:
            total_budget = self.proc_module.get_param_value("totalbudget", request_params)
            max_unit_valuation = self.proc_module.get_param_value("maxvalue", request_params)
            quantity = self.proc_module.get_param_value("quantity", request_params)

            budget_by_auction = total_budget / len(auctions)
            valuation_by_auction = max_unit_valuation / len(auctions)

            self.logger.debug("after setting up parameters")
            list_return = []
            for auction_key in auctions:
                bidding_object = self.create_bidding_object(auction_key, quantity, budget_by_auction,
                                                            valuation_by_auction, start, stop)

                list_return.append(bidding_object)

            self.logger.debug("ending execute user")
            return list_return
        except Exception as e:
            self.logger.error(str(e))

    def reset(self):
        print('reset')
