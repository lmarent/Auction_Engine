from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_field import IpapField
from foundation.field_def_manager import FieldDefManager
from foundation.config_param import ConfigParam
from foundation.singleton import Singleton
from foundation.parse_format import ParseFormats
from foundation.field_def_manager import DataType

import uuid
from datetime import datetime


class AllocProc:
    def __init__(self, bidding_object_key: str, element_name: str, session_id:str, quantity: float, sell_price: float):
        self.bidding_object_key = bidding_object_key
        self.element_name = element_name
        self.session_id = session_id
        self.quantity = quantity
        self.sell_price = sell_price

class ProcModule(metaclass=Singleton):

    def __init__(self):
        self.field_container = IpapFieldContainer()
        self.field_container.initialize_reverse()
        self.field_container.initialize_forward()
        self.field_def_manager = FieldDefManager()

    def get_param_value(self, field_name:str, params: dict):
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
