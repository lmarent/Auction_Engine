from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainerSingleton
from python_wrapper.ipap_template_container import IpapTemplateContainer
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_template import UnknownField
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_template import ObjectType
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_data_record import IpapDataRecord


from foundation.auction import Auction
from foundation.auction import Action
from foundation.ipap_message_parser import IpapMessageParser
from foundation.ipap_message_parser import IpapObjectKey
from foundation.auctioning_object import AuctioningObjectState
from foundation.parse_format import ParseFormats


class IpapAuctionParser(IpapMessageParser):

    def __init__(self, domain):
        super(IpapAuctionParser, self).__init__(domain)
        self.ipap_template_container = IpapTemplateContainerSingleton()

    def verify_insert_template(self, template: IpapTemplate, ipap_template_container: IpapTemplateContainer):
        """
        Verifies and in case of not included before inserts the template given in the template container

        :param template: template to include
        :param ipap_template_container: template container where templates should be verified.
        """
        # Insert templates in case of not created in the template container.
        try:

            template_ret = ipap_template_container.get_template(template.get_template_id())
            if not template_ret.is_equal(template):
                raise ValueError("Data Template {0} given is different from the template already stored".format(
                    template.get_template_id()))

        except ValueError:
            ipap_template_container.add_template(template)

    def parse_auction(self, templates: list, data_records: list,
                      ipap_template_container: IpapTemplateContainer) -> Auction:
        """
        Parse an auction from the ipap_message

        :param templates: templates for the auction
        :param data_records: records for the auction
        :param ipap_template_container: template container where we have to include the templates.
        :return: auction parsed.
        """
        data_template = None
        opts_template = None
        template_fields = []
        nbr_data_read = 0
        nbr_option_read = 0

        for template in templates:
            self.getTemplateFields(template, template_fields)
            if template.get_type() == TemplateType.IPAP_SETID_AUCTION_TEMPLATE:
                data_template = template
            elif template.get_type() == TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE:
                opts_template = template

        if (data_template is None):
            raise ValueError("The message is incomplete Data template was not included")

        if (opts_template is None):
            raise ValueError("The message is incomplete Options template was not included")


        # Verify templates
        self.verify_insert_template(data_template, ipap_template_container)
        self.verify_insert_template(opts_template, ipap_template_container)

        # Read data records
        for data_record in data_records:
            template_id = data_record.get_template_id()
            # Read a data record for a data template
            if template_id == data_template.get_template_id():
                data_misc = self.read_record(data_template, data_record)
                auction_key = self.extract_param('auctionid', data_misc)
                auction_status = self.extract_param('status', data_misc)
                resource_key = self.extract_param('resourceid', data_misc)
                template_list = self.extract_param('templatelist', data_misc)
                nbr_data_read = nbr_data_read + 1

            if template_id == opts_template.get_template_id():
                opts_misc = self.read_record(opts_template, data_record)
                action_name = self.extract_param('algoritmname', data_misc)
                nbr_option_read = nbr_option_read + 1

        if nbr_data_read > 1:
            raise ValueError("The message included more than one data template")

        if nbr_data_read == 0:
            raise ValueError("The message not included  a data template")

        if nbr_option_read > 1:
            raise ValueError("The message included more than one options template")

        if nbr_option_read == 0:
            raise ValueError("The message not included  a options template")

        action = Action(action_name.value, True, opts_misc)
        auction = Auction(auction_key.value, resource_key.value, action, data_misc )
        auction.set_state(AuctioningObjectState(ParseFormats.parse_int(auction_status.value)))
        template_ids = template_list.value.split(',')

        for template_sid in template_ids:
            template = ipap_template_container.get_template(ParseFormats.parse_int(template_sid))

            auction.set_bidding_object_template(template.get_object_type(template.get_type()),
                                                template.get_type(), template.get_template_id())

        return auction

    def parse(self, ipap_message: IpapMessage, ipap_template_container: IpapTemplateContainer):

        # Splits the message by object.
        object_templates, object_data_records, templates_not_related = self.split(ipap_message)

        # insert new templates not related (for example bidding templates to use for the auction) to the object.
        for template_id in templates_not_related:
            if not ipap_template_container.exists_template(template_id):
                ipap_template_container.add_template(templates_not_related[template_id])

        # loop through data records and parse the auction data
        for object_key in object_data_records:
            if object_key.get_key() == ObjectType.IPAP_AUCTION:
                self.parse_auction(object_key, object_templates[object_key], object_data_records[object_key])


    def get_non_mandatoty_fields(self, action: Action, mandatory_fields: list) -> list:
        """
        Gets non mandatory fields from the action's config items.

        :param action: action associated with the auction
        :param mandatory_fields: mandatory fields for an option template.
        :return: non_mandatory field list.
        """
        non_mandatory = []

        items = action.get_config_params()
        for item in items.values():
            field = self.field_def_manager.get_field(item.name)

            # Checks it is not a mandatory field.
            is_mandatory: bool = False
            for mandatory_field in mandatory_fields:
                if mandatory_field.get_eno() == field['eno'] and mandatory_field.get_ftype() == field['ftype']:
                    is_mandatory = True
                    break

            if not is_mandatory:
                non_mandatory.append(IpapFieldKey(field['eno'], field['ftype']))

        return non_mandatory

    def insert_auction_data_record(self, template: IpapTemplate, auction: Auction,
                                   message: IpapMessage, use_ipv6: bool, s_address: str,
                                   port: int):
        """
        Adds the option data record template associated with the option data auction template

        :param template template used for the data record.
        :param auction  auction being included in the message.
        :param message: message being built.
        :param use_ipv6: whether or not it use ipv6
        :param s_address: source address
        :param port: source port
        """
        ipap_data_record = IpapDataRecord(obj=None, templ_id=template.get_template_id())

        # Insert the auction id field.
        self.insert_string_field('auctionid', auction.get_key(), ipap_data_record)

        # Add the Record Id
        self.insert_string_field('recordid', "Record_1", ipap_data_record)

        # Add the Status
        self.insert_integer_field('status', auction.get_state().value, ipap_data_record)

        # Add the IP Version
        if use_ipv6:
            ipversion = 6
        else:
            ipversion = 4
        self.insert_integer_field('ipversion', ipversion, ipap_data_record)

        # Add the Ipv6 Address value
        if use_ipv6:
            self.insert_ipv6_field('dstipv6', s_address, ipap_data_record)
        else:
            self.insert_ipv6_field('dstipv6', "0:0:0:0:0:0:0:0", ipap_data_record)

        # Add the Ipv4 Address value
        if use_ipv6:
            self.insert_ipv4_field('dstipv4', "0.0.0.0", ipap_data_record)
        else:
            self.insert_ipv4_field('dstipv4', s_address, ipap_data_record)

        # Add destination port
        self.insert_integer_field('dstauctionport', port, ipap_data_record)

        # Add the resource Id.
        self.insert_string_field('resourceid', auction.get_resource_key(), ipap_data_record)

        # Add the start time - Unix time is seconds from 1970-1-1 .
        self.insert_datetime_field('start', auction.get_start(), ipap_data_record)

        # Add the end time.
        self.insert_datetime_field('stop', auction.get_stop(), ipap_data_record)

        # Add the interval. How much time between executions (seconds).
        u_interval = auction.get_interval().interval
        self.insert_integer_field('interval', u_interval, ipap_data_record)

        # Add the template list.
        self.insert_string_field('templatelist', auction.get_template_list(), ipap_data_record)

        message.include_data(template.get_template_id(), ipap_data_record)

    def insert_option_data_record(self, template: IpapTemplate, auction: Auction, message: IpapMessage):
        """
        Inserts templates associated with the auction

        :param template    auction template
        :param auction     auction being included in the message.
        :param message:    message being built.
        :return:
        """
        ipap_options_record = IpapDataRecord(obj=None, templ_id=template.get_template_id())

        # Add the auction Id
        self.insert_string_field('auctionid', auction.get_key(), ipap_options_record)

        # Add the Record Id
        self.insert_string_field('recordid', "Record_1", ipap_options_record)

        # Add the action
        self.insert_string_field('algoritmname', auction.action.name, ipap_options_record)

        # Adds non mandatory fields.
        option_fields = template.get_template_type_mandatory_field(TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE)

        items = auction.action.get_config_params()
        for item in items.values():
            field = self.field_def_manager.get_field(item.name)

            # Checks it is not a mandatory field.
            is_mandatory: bool = False
            for mandatory_field in option_fields:
                if mandatory_field.get_eno() == field['eno'] and mandatory_field.get_ftype() == field['ftype']:
                    is_mandatory = True
                    break

            if not is_mandatory:
                # check the field is a valid field for the message
                field_act = self.field_container.get_field(field['eno'], field['ftype'])
                act_f_value = field_act.parse(item.value)
                ipap_options_record.insert_field(field['eno'], field['ftype'], act_f_value)

        message.include_data(template.get_template_id(), ipap_options_record)

    def insert_auction_templates(self, template: IpapTemplate, auction: Auction, message: IpapMessage):
        """
        Inserts templates associated with the auction

        :param template    auction template
        :param auction     auction being included in the message.
        :param message:    message being built.
        :return:
        """
        for i in range(1, ObjectType.IPAP_MAX_OBJECT_TYPE.value):
            list_types = template.get_object_template_types(ObjectType(i))
            for templ_type in list_types:
                templ_id = auction.get_bidding_object_template(ObjectType(i), templ_type)
                message.make_template(self.ipap_template_container.get_template(templ_id))

    def get_ipap_message_auction(self, auction: Auction, use_ipv6: bool, s_address: str, port: int, message: IpapMessage):
        """
        Updates the ipap_message given as parameter with the infomation of the auction

        :param auction: auction to include in the message
        :param use_ipv6: whether or not it use ipv6
        :param s_address: source address
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
        optional_fields = self.get_non_mandatoty_fields(auction.action, mandatory_fields)

        option_template.set_max_fields(option_template.get_num_fields() + len(optional_fields))
        for field in optional_fields:
            ipap_field = self.field_container.get_field(field.get_eno(), field.get_ftype())
            option_template.add_field(ipap_field.get_length(), UnknownField.KNOWN, True, ipap_field)

        message.make_template(option_template)
        self.insert_auction_templates(auction_template, auction, message)
        self.insert_auction_data_record(auction_template, auction, message,
                                        use_ipv6, s_address, port)
        self.insert_option_data_record(option_template, auction, message)

    def get_ipap_message(self, auctions: list, use_ipv6: bool, s_address: str, port: int) -> IpapMessage:
        """
        Gets an ipap_message to transfer the information of the auctions given as parameter.

        :param auctions: List of auctions to convert to a message
        :param use_ipv6: whether or not it use ipv6
        :param s_address: source address
        :param port: source port
        :return: ipap message with auction information.
        """
        message = IpapMessage(self.domain, IpapMessage.IPAP_VERSION, True)

        for auction in auctions:
            self.get_ipap_message_auction(auction, use_ipv6, s_address, port, message)

        message.output()
        return message
