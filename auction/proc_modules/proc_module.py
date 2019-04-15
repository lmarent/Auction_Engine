from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_field import IpapField
from foundation.field_def_manager import FieldDefManager
from foundation.config_param import ConfigParam
from foundation.singleton import Singleton
from foundation.parse_format import ParseFormats
from foundation.field_def_manager import DataType
from foundation.bidding_object import BiddingObject
from foundation.auction import AuctioningObjectType

import uuid
from datetime import datetime
from typing import Dict
from typing import DefaultDict
from collections import defaultdict


class AllocProc:
    def __init__(self, auction_key: str, bidding_object_key: str, element_name: str,
                 session_id: str, quantity: float, price: float):
        self.auction_key = auction_key
        self.bidding_object_key = bidding_object_key
        self.element_name = element_name
        self.session_id = session_id
        self.quantity = quantity
        self.original_price = price


class ProcModule(metaclass=Singleton):

    def __init__(self):
        self.field_container = IpapFieldContainer()
        self.field_container.initialize_reverse()
        self.field_container.initialize_forward()
        self.field_def_manager = FieldDefManager()

    def get_param_value(self, field_name: str, params: dict):
        """
        Get the value of a parameter
        :param field_name: name of the parameter
        :param params: parameters
        :return: value of the parameter.
        """
        field_def = self.field_def_manager.get_field(field_name)
        if field_def['type'] == DataType.DOUBLE:
            return ParseFormats.parse_double(params[field_name].get_exact_field_value())
        elif field_def['type'] == DataType.UINT32:
            return ParseFormats.parse_ulong(params[field_name].get_exact_field_value())
        elif field_def['type'] == DataType.STRING:
            return params[field_name].get_exact_field_value()
        elif field_def['type'] == DataType.UINT64:
            return ParseFormats.parse_ulong(params[field_name].get_exact_field_value())
        elif field_def['type'] == DataType.IPV4ADDR:
            return ParseFormats.parse_ipaddress(params[field_name].get_exact_field_value())
        elif field_def['type'] == DataType.IPV6ADDR:
            return ParseFormats.parse_ipaddress(params[field_name].get_exact_field_value())
        elif field_def['type'] == DataType.UINT8:
            return ParseFormats.parse_uint8(params[field_name].get_exact_field_value())
        elif field_def['type'] == DataType.FLOAT:
            return ParseFormats.parse_float(params[field_name].get_exact_field_value())
        else:
            raise ValueError("Invalid type {0}".format(field_def['type'].lower()))

    def insert_field(self, field_def: dict, value: str, config_params: dict):
        """
        Inserts a new field in a config param dictionary
        :param field_def: field definition
        :param value: value to be assigned to the field
        :param config_params: dictinary being fill.
        """
        field = ConfigParam(name=field_def['key'], p_type=field_def['type'], value=value)
        config_params[field.name] = field

    def insert_string_field(self, field_name: str, value: str, config_params: dict):
        """
        Inserts a field value in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param config_params: dictionary where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        self.insert_field(field_def, value, config_params)

    def insert_integer_field(self, field_name: str, value: int, config_params: dict):
        """
        Inserts a field value in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param config_params: dictionary where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(
            int(field_def['eno']), int(field_def['ftype']))

        if field.get_length() == 1:
            self.insert_field(field_def, field.write_value(field.get_ipap_field_value_uint8(value)), config_params)
        elif field.get_length() == 2:
            self.insert_field(field_def, field.write_value(field.get_ipap_field_value_uint16(value)), config_params)
        elif field.get_length() == 4:
            self.insert_field(field_def, field.write_value(field.get_ipap_field_value_uint32(value)), config_params)
        elif field.get_length() == 8:
            self.insert_field(field_def, field.write_value(field.get_ipap_field_value_uint64(value)), config_params)

    def insert_float_field(self, field_name: str, value: float, config_params: dict):
        """
        Inserts a field value in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param config_params: dictionary where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(
            int(field_def['eno']), int(field_def['ftype']))
        self.insert_field(field_def, field.write_value(field.get_ipap_field_value_float(value)), config_params)

    def insert_double_field(self, field_name: str, value: float, config_params: dict):
        """
        Inserts a field value (double) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param config_params: dictionary where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(
            int(field_def['eno']), int(field_def['ftype']))
        self.insert_field(field_def, field.write_value(field.get_ipap_field_value_double(value)), config_params)

    def insert_ipv4_field(self, field_name: str, value: str, config_params: dict):
        """
        Inserts a field value (ip address 4) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param config_params: dictionary where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(int(field_def['eno']), int(field_def['ftype']))
        value_encoded = value.encode('ascii')
        self.insert_field(field_def, field.write_value(field.get_ipap_field_value_ipv4(value_encoded)), config_params)

    def insert_ipv6_field(self, field_name: str, value: str, config_params: dict):
        """
        Inserts a field value (ip address 6) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param config_params: dictionary where the field is going to be inserted.
        """
        field_def = self.field_def_manager.get_field(field_name)
        field: IpapField = self.field_container.get_field(int(field_def['eno']), int(field_def['ftype']))
        value_encoded = value.encode('ascii')
        self.insert_field(field_def, field.write_value(field.get_ipap_field_value_ipv6(value_encoded)), config_params)

    def insert_datetime_field(self, field_name: str, value: datetime, config_params: dict):
        """
        Inserts a field value (datetime) in the data record given as parameter

        :param field_name: field to be inserted
        :param value: value to insert
        :param config_params: dictionary where the field is going to be inserted.
        """
        seconds = int((value - datetime.fromtimestamp(0)).total_seconds())
        self.insert_integer_field(field_name, seconds, config_params)

    def get_bidding_object_id(self) -> str:
        """
        Generates a nex bidding object id
        :return:
        """
        id = uuid.uuid1()
        return str(id)

    @staticmethod
    def make_key(auction_key: str, bid_key: str) -> str:
        """
        Make the key of an allocation from the auction key and bidding object key

        :param auction_key: auction key
        :param bid_key: bidding object key
        :return:
        """
        return auction_key + '-' + bid_key

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
        elements = dict()
        config_elements = dict()

        # Insert quantity ipap_field
        record_id = "record_1"
        self.insert_string_field("recordid", record_id, config_elements)
        self.insert_float_field("quantity", quantity, config_elements)
        self.insert_double_field("unitprice", price, config_elements)
        elements[record_id] = config_elements

        # construct the interval with the allocation, based on start datetime
        # and interval for the requesting auction

        options = dict()
        option_id = 'option_1'
        config_options = dict()

        self.insert_string_field("recordid", option_id, config_elements)
        self.insert_datetime_field("start", start, config_options)
        self.insert_datetime_field("stop", stop, config_options)
        options[option_id] = config_options

        bidding_object_id = self.proc_module.get_bidding_object_id()
        bidding_object_key = str(self.domain) + '.' + bidding_object_id
        alloc = BiddingObject(auction_key, bidding_object_key, AuctioningObjectType.ALLOCATION, elements, options)

        # All objects must be inherit the session from the bid.
        alloc.set_session(session_id)

        return alloc

    @staticmethod
    def increment_quantity_allocation(allocation: BiddingObject, quantity: float):
        """
        Increments the quantity assigned to an allocation

        :param allocation: allocation to be incremented
        :param quantity: quantity to increment
        """
        elements = allocation.elements

        # there is only one element
        updated = False
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
            updated = True
            break

        if not updated:
            raise ValueError("Field quantity was not included in the allocation")

    @staticmethod
    def get_allocation_quantity(bidding_object: BiddingObject) -> float:
        """

        :param bidding_object:
        :return:
        """
        temp_qty = 0
        elements = bidding_object.elements

        # there is only one element.
        for element_name in elements:
            config_dict = elements[element_name]
            # remove the field for updating quantities
            field: ConfigParam = config_dict['quantity']
            temp_qty = ParseFormats.parse_float(field.value)
            break

        return temp_qty

    @staticmethod
    def change_allocation_price(allocation: BiddingObject, price: float):
        """
        Change allocation price

        :param allocation: allocation to be incremented
        :param price: price to be assigned
        """
        elements = allocation.elements

        # there is only one element
        updated = False
        for element_name in elements:
            config_dict = elements[element_name]
            # remove the field for updating quantities
            field: ConfigParam = config_dict.pop('unitprice')
            # Insert again the field.
            fvalue = str(price)
            field.value = fvalue
            config_dict[field.name] = field
            updated = True
            break

        if not updated:
            raise ValueError("Field price was not included in the allocation")

    @staticmethod
    def get_bid_price(bidding_object: BiddingObject) -> float:
        """
        Gets the bid price from a bidding object

        :param bidding_object: bidding object from where to get the price
        :return: bid price
        """
        unit_price = -1

        elements = bidding_object.elements
        for element_name in elements:
            config_dict = elements[element_name]
            unit_price = float(config_dict['unitprice'].value)
            break
        return unit_price

    @staticmethod
    def calculate_requested_quantities(bidding_objects: Dict[str, BiddingObject]) -> float:
        """
        Calculates request quantity for a bunch of bidding objects

        :param bidding_objects: bidding objects to aggregate the requested quantity
        :return: total sum of quantities requested on bidding objects
        """
        sum_quantity = 0
        for bidding_object_key in bidding_objects:
            bidding_object = bidding_objects[bidding_object_key]
            elements = bidding_object.elements
            for element_name in elements:
                config_dict = elements[element_name]
                quantity = float(config_dict['quantity'].value)
                sum_quantity = sum_quantity + quantity

        return sum_quantity

    def separate_bids(self, bidding_objects: Dict[str, BiddingObject], bl: float) -> (Dict[str, BiddingObject],
                                                                                      Dict[str, BiddingObject]):
        """
        Split bids as low budget and high budget bids

        :param bidding_objects: bidding object to split
        :param bl: low budget limit
        :return: a dictionary for low budget bids, another dictionary for high budget bids.
        """
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

        return bids_low, bids_high

    def sort_bids_by_price(self, bids: Dict[str, BiddingObject], discriminatory_price: float = 0,
                           subsidy: float = 1) -> DefaultDict[float, list]:
        """
        sort bids by price in descending order

        :return:
        """
        ordered_bids: DefaultDict[float, list] = defaultdict(list)
        for bidding_object_key in bids:
            bidding_object = bids[bidding_object_key]
            elements = bidding_object.elements
            for element_name in elements:
                config_params = elements[element_name]
                price = ParseFormats.parse_float(config_params["unitprice"].value)
                quantity = ParseFormats.parse_float(config_params["quantity"].value)
                alloc = AllocProc(bidding_object.get_auction_key(), bidding_object.get_key(),
                                  element_name, bidding_object.get_session(), quantity, price)
                # applies the subsidy if it was given,
                if discriminatory_price > 0:
                    if price < discriminatory_price:
                        price = price * subsidy

                ordered_bids[price].append(alloc)

        return ordered_bids
