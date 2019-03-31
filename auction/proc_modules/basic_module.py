from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.parse_format import ParseFormats
from foundation.config_param import ConfigParam
from foundation.bidding_object import BiddingObject
from foundation.auction import AuctioningObjectType

from datetime import datetime
from utils.auction_utils import log
from typing import Dict


class BasicModule(Module):


    def __init__(self, module_name:str, module_file:str, module_handle, config_group:str):
        super(BasicModule,self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}
        self.logger = log().get_logger()
        self.bandwidth = 0
        self.reserved_price = 0
        self.domain = 0

    def init_module(self, config_param_list:Dict[str, ConfigParam]):
        self.logger.debug('in init_module')
        self.config_param_list = config_param_list
        self.domain = config_param_list['domainid']

    def get_resource_avalability(self):
        self.logger.debug('Starting getResourceAvailability')

        self.bandwidth = ParseFormats.parse_float(self.config_param_list['bandwidth'].value)

        if self.bandwidth <= 0:
            raise ValueError("bas init module - The given bandwidth parameter is incorrect");

        return self.bandwidth

    def get_reserved_price(self):
        self.logger.debug('Starting get_reserved_price')

        self.reserved_price = ParseFormats.parse_double(self.config_param_list['reserveprice'].value)

        if (self.reserved_price < 0):
            raise ValueError("bas init module - The given reserve price is incorrect")

        return self.reserved_price

    def make_key(self, auction_key: str, bid_key: str) -> str:
        return auction_key + '-' + bid_key

    def create_allocation(self, session_id: str, auction_key: str, start: datetime,
                                stop: datetime, quantity: float, price: float):

        self.logger("bas module: start create allocation")

        elements = dict()
        config_elements = dict()

        # Insert quantity ipap_field
        record_id = "record_1";
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

        return alloc;

    def increment_quantity_allocation(self):

    def calculate_requested_quantities(self):

    def get_bid_price(self):

    def separate_bids(self):

    def destroy_module(self):
        print ('in destroy_module')

    def execute(self, auction_key: str, start:datetime, stop:datetime, bids: dict) -> dict:
        print('in execute')
        return {}

    def execute_user(self, request_params: Dict[str, FieldValue], auctions: dict,
                     start: datetime, stop: datetime) -> list:
        print('in execute_user')
        pass

    def reset(self):
        print('in reset')