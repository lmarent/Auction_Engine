from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_template_container import IpapTemplateContainer
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_template import UnknownField
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_template import ObjectType
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_field import IpapField

from foundation.auction import Auction
from foundation.auction import Action
from foundation.field_def_manager import FieldDefManager

import time


class MapiAuctionParser:

    def __init__(self, domain):
        self.domain = domain
        self.ipap_template_container = IpapTemplateContainer()
        self.field_manager = FieldDefManager()
        self.field_container = IpapFieldContainer()
        self.field_container.initialize_reverse()
        self.field_container.initialize_forward()

    def get_non_mandatoty_fields(self, action: Action, mandatory_fields: list, message: IpapMessage) -> list:
        """
        Gets non mandatory fields from the action's config items.

        :param action: action associated with the auction
        :param mandatory_fields: mandatory fields for an option template.
        :param message: message being built.
        :return:
        """
        non_mandatory = []

        items = action.get_config_params()
        for item in items:
            field = self.field_manager.get_field(item.name)

            # Checks it is not a mandatory field.
            is_mandatory = False
            for mandatory_field in mandatory_fields:
                if mandatory_field.get_eno() == field['eno'] and mandatory_field.get_ftype() == field['ftype']:
                    is_mandatory = True
                    break

            if is_mandatory == False:
                # check the field is a valid field for the message
                message.get_field_definition(field['eno'], field['ftype'])
                non_mandatory.append(IpapFieldKey(field['eno'], field['ftype']))

    def insert_string_field(self, field_def, value: str, record: IpapDataRecord):
        """
        Inserts a field value in the data record given as parameter

        :param field_def: field to be inserted
        :param value: value to insert
        :param record: data record where the field is going to be inserted.
        """
        field: IpapField = self.field_container.get_field(
            int(field_def['eno']), int(field_def['ftype']))
        record.insert_field(int(field_def['eno']), int(field_def['ftype']),
                                 field.get_ipap_field_value_string(value))

    def


    def insert_auction_data_record(self, template: IpapTemplate, auction: Auction,
                                   message: IpapMessage, useIpv6: bool, saddress_ipv4: str, saddress_ipv6: str,
                                   port: int):
        """
        Adds the option data record template associated with the option data auction template

        :param message:    message being built.
        :return:
        """
        ipap_data_record = IpapDataRecord(template.get_template_id())

        # Insert the auction id field.
        field_def = self.field_manager.get_field('auctionid')
        self.insert_string_field(field_def, auction.get_key(), ipap_data_record)

        # Add the Record Id
        field_def = self.field_manager.get_field('recordid')
        id_record_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_record = id_record_field.get_ipap_value_field("Record_1", len("Record_1"))
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_record)

        # Add the Status
        field_def = self.field_manager.get_field('status')
        id_status_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        state = auction.get_state().value
        f_val_status = id_status_field.get_ipap_value_field(state)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_val_status)

        # Add the IP Version
        field_def = self.field_manager.get_field('ipversion')
        ip_version_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        if useIpv6:
            ipversion = 6
        else:
            ipversion = 4
        f_val_ip_version = ip_version_field.get_ipap_value_field(ipversion)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_val_ip_version)

        # Add the Ipv6 Address value
        field_def = self.field_manager.get_field('dstipv6')
        ip_addr6_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        if useIpv6:
            f_value_ipAddr6 = ip_addr6_field.parse_ip_address_6(saddress_ipv6)
        else:
            f_value_ipAddr6 = ip_addr6_field.parse_ip_address_6("0:0:0:0:0:0:0:0")
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_ipAddr6)

        # Add the Ipv4 Address value
        field_def = self.field_manager.get_field('dstipv4')
        ip_addr4_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        if useIpv6:
            f_value_ipAddr4 = ip_addr4_field.parse_ip_address_4("0.0.0.0")
        else:
            f_value_ipAddr4 = ip_addr6_field.parse_ip_address_4(saddress_ipv4)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_ipAddr4)

        # Add destination port
        field_def = self.field_manager.get_field('dstauctionport')
        port_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_port = port_field.get_ipap_value_field(port)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_port)

        # Add the resource Id.
        field_def = self.field_manager.get_field('resourceid')
        resource_id_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_resource_id = resource_id_field.parse_string(auction.get_resource_key())
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_resource_id)

        # Add the start time - Unix time is seconds from 1970-1-1 .
        field_def = self.field_manager.get_field('start')
        unix_time = time.mktime(auction.get_start().timetuple())
        id_start_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_start = id_start_field.get_ipap_value_field(unix_time)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_start)

        # Add the end time.
        field_def = self.field_manager.get_field('stop')
        id_stop_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        unix_time = time.mktime(auction.get_stop().timetuple())
        f_value_stop = id_stop_field.get_ipap_value_field(unix_time)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_stop)

        # Add the interval. How much time between executions (seconds).
        field_def = self.field_manager.get_field('interval')
        u_interval = auction.get_interval().interval
        id_interval_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_interval = id_interval_field.get_ipap_value_field(u_interval)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_interval)

        # Add the template list.
        field_def = self.field_manager.get_field('templatelist')
        template_list = auction.get_template_list()
        template_list_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_tlist = template_list_field.parseString(template_list)
        ipap_data_record.insert_field(field_def['eno'], field_def['ftype'], f_value_tlist)

        message.include_data(template.get_template_id(), ipap_data_record)

    def insert_option_data_record(self, template: IpapTemplate, auction: Auction, message: IpapMessage):
        """
        Inserts templates associated with the auction

        :param template    auction template
        :param auction     auction being included in the message.
        :param message:    message being built.
        :return:
        """
        ipap_options_record = IpapDataRecord(template.get_template_id())

        # Add the auction Id
        field_def = self.field_manager.get_field('auctionid')
        id_auction_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_act_id = id_auction_field.get_ipap_value_field(auction.get_key(), len(auction.get_key()))
        ipap_options_record.insert_field(field_def['eno'], field_def['ftype'], f_value_act_id)

        # Add the Record Id
        field_def = self.field_manager.get_field('recordid')
        id_record_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_record = id_record_field.get_ipap_value_field("Record_1", len("Record_1"))
        ipap_options_record.insert_field(field_def['eno'], field_def['ftype'], f_value_record)

        # Add the action
        field_def = self.field_manager.get_field('algoritmname')
        id_action_field = message.get_field_definition(field_def['eno'], field_def['ftype'])
        f_value_action = id_action_field.get_ipap_value_field(auction.action.name, len(auction.action.name))
        ipap_options_record.insert_field(field_def['eno'], field_def['ftype'], f_value_action)

        # Adds non mandatory fields.
        option_fields = template.get_template_type_mandatory_field(TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE)

        items = auction.action.get_config_params()
        for item in items:
            field = self.field_manager.get_field(item.name)

            # Checks it is not a mandatory field.
            is_mandatory = False
            for mandatory_field in option_fields:
                if mandatory_field.get_eno() == field['eno'] and mandatory_field.get_ftype() == field['ftype']:
                    is_mandatory = True
                    break

            if is_mandatory == False:
                # check the field is a valid field for the message
                field_act = message.get_field_definition(field['eno'], field['ftype'])
                act_f_value = field_act.parse(item.value)
                ipap_options_record.insert_field(IpapFieldKey(field['eno'], field['ftype']))

        message.include_data(template.get_template_id(), ipap_options_record)

    def insert_auction_templates(self, template: IpapTemplate, auction: Auction, message: IpapMessage):
        """
        Inserts templates associated with the auction

        :param template    auction template
        :param auction     auction being included in the message.
        :param message:    message being built.
        :return:
        """
        for i in range(1, ObjectType.IPAP_MAX_OBJECT_TYPE):
            list_types = template.get_object_template_types(i)
            for templ_type in list_types:
                templ_id = auction.get_bidding_object_template(templ_type)
                message.make_template(self.ipap_template_container.get_template(templ_id))

    def get_ipap_message_auction(self, auction: Auction, useIpv6: bool,
                                 saddress_ipv4: str, saddress_ipv6: str,
                                 port: int, message: IpapMessage):
        """
        Updates the ipap_message given as parameter with the infomation of the auction

        :param auction: auction to include in the message
        :param useIpv6: whether or not it use ipv6
        :param sAddressIpv4: source address in ipv4
        :param sAddressIpv6: source address in ipv6
        :param port: source port
        :param message: ipap message to modify an include the information.
        """
        auction_template_id = auction.get_auction_data_template()
        auction_template = self.ipap_template_container.get_template(auction_template_id)
        message.make_template(auction_template)

        option_template_id = auction.get_option_auction_template()
        option_template = self.ipap_template_container.get_template(option_template_id)

        # Following lines are used for inserting only non mandatory fields
        mandatory_fields = option_template.get_template_type_mandatory_field(option_template.get_type())
        optional_fields = self.get_non_mandatoty_fields(auction.action, mandatory_fields, message)

        option_template.set_max_fields(option_template.get_num_fields() + len(optional_fields))
        for field in optional_fields:
            ipap_field = field_container.get_field(field.get_eno(), field.get_ftype())
            option_template.add_field(ipap_field.get_length(), UnknownField.KNOWN, True, ipap_field)

        message.make_template(option_template)
        self.insert_auction_templates(auction_template, auction, message)
        self.insert_auction_data_record(auction_template, auction, message, useIpv6, saddress_ipv4, saddress_ipv6, port)
        self.insert_option_data_record(self, option_template, auction, message)

    def get_ipap_message(self, auctions: list, useIpv6: bool,
                         sAddressIpv4: str, sAddressIpv6: str,
                         port: int) -> IpapMessage:
        """
        Gets an ipap_message to transmit the information of the auctions given as parameter.

        :param auctions: List of auctions to convert to a message
        :param useIpv6: whether or not it use ipv6
        :param sAddressIpv4: source address in ipv4
        :param sAddressIpv6: source address in ipv6
        :param port: source port
        :return: ipap message with auction information.
        """
        message = IpapMessage(self.domain, IpapMessage.IPAP_VERSION, True)

        for auction in auctions:
            self.get_ipap_message_auction(message)

        message.output()
        return message
