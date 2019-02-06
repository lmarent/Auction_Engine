from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_template_container import IpapTemplateContainer
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_template import UnknownField

from foundation.auction import Auction
from foundation.auction import Action
from foundation.field_def_manager import FieldDefManager


class MapiAuctionParser:

    def __init__(self, domain):
        self.domain = domain
        self.ipap_template_container = IpapTemplateContainer()
        self.field_manager = FieldDefManager()

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

    def get_ipap_message_auction(self, auction: Auction, useIpv6: bool,
                         sAddressIpv4: str, sAddressIpv6: str,
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
        field_container = IpapFieldContainer()
        field_container.initialize_reverse()
        field_container.initialize_forward()

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
