from foundation.module import Module
from foundation.auction import Auction
from foundation.bidding_object import BiddingObject

from proc_modules.proc_module import ProcModule
from python_wrapper.ipap_template import ObjectType

from datetime import datetime


class basic_module_user(Module):

    def __init__(self, module_name:str, module_file:str, module_handle, domain: int, config_group:str):
        super(basic_module_user,self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}
        self.domain = domain
        self.proc_module = ProcModule()

    def init_module(self, config_param_list: dict):
        self.config_param_list = config_param_list

    def check_parameters(self, field_definitions, request_params):
        required_fields = set()
        required_fields.add(self.proc_module.field_def_manager.get_field("quantity"))
        required_fields.add(self.proc_module.field_def_manager.get_field("totalbudget"))
        required_fields.add(self.proc_module.field_def_manager.get_field("maxvalue"))

        for field in required_fields:
            if field['key'] not in request_params:
                raise ValueError("basic module: ending check - it does not pass the check, \
                                 field not included {0}".format(field['key']))

    def create_bidding_object(self, auction: Auction, quantity: float, unit_budget: float,
                              unit_price: float, start: datetime, stop: datetime) -> BiddingObject:


        if unit_budget < unit_price:
            unit_price = unit_budget

        # build the elements of the bidding object
        elements = dict()
        config_elements = dict()
        record_id = "record_1"
        self.proc_module.insert_string_field("recordid", record_id, config_elements)
        self.proc_module.insert_double_field("quantity", quantity, config_elements)
        self.proc_module.insert_double_field("unitprice", unit_price, config_elements)
        elements[record_id] = config_elements

        # build the options (time intervals)
        options = dict()
        option_id = 'option_1'
        config_options = dict()
        self.proc_module.insert_datetime_field("start", start, config_options)
        self.proc_module.insert_datetime_field("stop", stop, config_options)
        options[option_id] = config_options

        id = self.proc_module.get_bidding_object_id()
        bidding_object_key = str(self.domain) + '.' + str(id)
        bidding_object = BiddingObject(auction.get_key(), bidding_object_key, ObjectType.IPAP_BID, elements, options)
        return bidding_object

    def destroy_module(self):
        pass

    def execute(self, auction_key: str, start:datetime, stop:datetime, bids: dict)  -> dict:
        return {}

    def execute_user(self, request_params: dict, auctions: list, start:datetime, stop:datetime) -> list:

        # TODO: Finish getting params from request_params.

        list_return = []
        for auction in auctions:
            bidding_object = self.create_bidding_object(auction, quantity, unit_budget, unit_price, start, stop)
            list_return.append(bidding_object)

        return list_return

    def reset(self):
        print('reset')