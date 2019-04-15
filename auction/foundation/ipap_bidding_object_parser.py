from python_wrapper.ipap_template import ObjectType
from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainer
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_data_record import IpapDataRecord

from foundation.ipap_message_parser import IpapMessageParser
from foundation.ipap_message_parser import IpapObjectKey
from foundation.bidding_object import BiddingObject
from foundation.auctioning_object import AuctioningObjectState
from foundation.parse_format import ParseFormats
from foundation.auction import Auction

from datetime import datetime


class IpapBiddingObjectParser(IpapMessageParser):

    def __init__(self, domain):
        super(IpapBiddingObjectParser, self).__init__(domain)

    @staticmethod
    def check_same_bidding_object(auction_key: str, bidding_object_key: str,
                                  auction_key_tmp: str, bidding_object_key_tmp: str) -> (str, str):
        """
        checks the same bidding objectis being refered in the message
        :param auction_key:
        :param bidding_object_key:
        :param auction_key_tmp:
        :param bidding_object_key_tmp:
        :return:
        """
        if auction_key is None:
            auction_key = auction_key_tmp
        else:
            if auction_key != auction_key_tmp:
                raise ValueError("The parte of the message is not for the same bidding object. original biddingobject \
                                    {0}-{1} and the bidding object given is {2}-{3}".format(auction_key,
                                                                                            bidding_object_key,
                                                                                            auction_key_tmp,
                                                                                            bidding_object_key_tmp))

        if bidding_object_key is None:
            bidding_object_key = bidding_object_key_tmp
        else:
            if bidding_object_key != bidding_object_key_tmp:
                raise ValueError("The parte of the message is not for the same bidding object. original biddingobject \
                                    {0}-{1} and the bidding object given is {2}-{3}".format(auction_key,
                                                                                            bidding_object_key,
                                                                                            auction_key_tmp,
                                                                                            bidding_object_key_tmp))
        return auction_key, bidding_object_key

    def parse_bidding_object(self, object_key: IpapObjectKey, templates: list, data_records: list,
                             ipap_template_container: IpapTemplateContainer) -> BiddingObject:
        """
        Parse a bidding object from the ipap_message

        :param templates: templates for the auction
        :param data_records: records for the auction
        :param ipap_template_container: template container where we have to include the templates.
        :return: bidding object parsed.
        """
        nbr_data_read = 0
        nbr_option_read = 0
        bidding_object_key = None
        auction_key = None
        s_bidding_object_type = None
        status = None

        data_template, opts_template = self.insert_auction_templates(object_key.get_object_type(),
                                                                     templates, ipap_template_container)

        # Read data records
        elements = {}
        for data_record in data_records:
            template_id = data_record.get_template_id()
            # Read a data record for a data template
            if template_id == data_template.get_template_id():
                data_misc = self.read_record(data_template, data_record)
                record_id = self.extract_param(data_misc, 'recordid').value
                elements[record_id] = data_misc
                # all records have the following same information.
                bidding_object_key_tmp = self.extract_param(data_misc, 'biddingobjectid').value
                auction_key_tmp = self.extract_param(data_misc, 'auctionid').value
                auction_key, bidding_object_key = self.check_same_bidding_object(auction_key, bidding_object_key,
                                                                            auction_key_tmp, bidding_object_key_tmp)
                s_bidding_object_type = self.extract_param(data_misc, 'biddingobjecttype').value
                status = self.extract_param(data_misc, 'status').value
                # a new record was read
                nbr_data_read = nbr_data_read + 1

            options = {}
            if template_id == opts_template.get_template_id():
                opts_misc = self.read_record(opts_template, data_record)
                record_id = self.extract_param(opts_misc, 'recordid').value
                auction_key_tmp = self.extract_param(opts_misc, 'auctionid').value
                bidding_object_key_tmp = self.extract_param(opts_misc, 'biddingobjectid').value
                auction_key, bidding_object_key = self.check_same_bidding_object(auction_key, bidding_object_key,
                                                                            auction_key_tmp, bidding_object_key_tmp)

                options[record_id] = opts_misc
                # a new record was read
                nbr_option_read = nbr_option_read + 1

        if nbr_data_read == 0:
            raise ValueError("A data template was not given")

        if nbr_option_read == 0:
            raise ValueError("An option template was not given")

        bidding_object_type = self.get_auctioning_object_type(self.parse_type(s_bidding_object_type))
        bidding_object = BiddingObject(auction_key, bidding_object_key, bidding_object_type, elements, options)
        status_val = ParseFormats.parse_int(status)
        bidding_object.set_state(AuctioningObjectState(status_val))

        return bidding_object

    def parse(self, ipap_message: IpapMessage, ipap_template_container: IpapTemplateContainer) -> list:

        bidding_object_ret = []

        # Splits the message by object.
        object_templates, object_data_records, templates_not_related = self.split(ipap_message)

        # loop through data records and parse the auction data
        for object_key in object_data_records:
            if object_key.get_object_type() in [ObjectType.IPAP_BID, ObjectType.IPAP_ALLOCATION]:
                bidding_object = self.parse_bidding_object(object_key, object_templates[object_key],
                                                           object_data_records[object_key], ipap_template_container)
                bidding_object_ret.append(bidding_object)

        return bidding_object_ret

    def include_data_record(self, template: IpapTemplate, bidding_object: BiddingObject, record_id: str,
                            config_params: dict, message: IpapMessage):

        ipap_data_record = IpapDataRecord(obj=None, templ_id=template.get_template_id())

        # Insert the auction id field.
        self.insert_string_field('auctionid', bidding_object.get_parent_key(), ipap_data_record)

        # Insert the bidding object id field.
        self.insert_string_field('biddingobjectid', bidding_object.get_key(), ipap_data_record)

        # Add the Record Id
        self.insert_string_field('recordid', record_id, ipap_data_record)

        # Add the Status
        self.insert_integer_field('status', bidding_object.get_state().value, ipap_data_record)

        # Add bidding_object type
        self.insert_integer_field('biddingobjecttype', bidding_object.get_type().value, ipap_data_record)

        # Adds non mandatory fields.
        mandatory_fields = template.get_template_type_mandatory_field(template.get_type())
        self.include_non_mandatory_fields(mandatory_fields, config_params, ipap_data_record)

        # Include the data record in the message.
        message.include_data(template.get_template_id(), ipap_data_record)

    def include_options_record(self, template: IpapTemplate, bidding_object: BiddingObject, record_id: str,
                               start: datetime, stop: datetime, config_params: dict, message: IpapMessage):

        ipap_record = IpapDataRecord(obj=None, templ_id=template.get_template_id())

        # Insert the auction id field.
        self.insert_string_field('auctionid', bidding_object.get_parent_key(), ipap_record)

        # Insert the bidding object id field.
        self.insert_string_field('biddingobjectid', bidding_object.get_key(), ipap_record)

        # Add the Record Id
        self.insert_string_field('recordid', record_id, ipap_record)

        # Add the start time - Unix time is seconds from 1970-1-1 .
        self.insert_datetime_field('start', start, ipap_record)

        # Add the end time.
        self.insert_datetime_field('stop', stop, ipap_record)

        # Adds non mandatory fields.
        mandatory_fields = template.get_template_type_mandatory_field(template.get_type())
        self.include_non_mandatory_fields(mandatory_fields, config_params, ipap_record)

        message.include_data(template.get_template_id(), ipap_record)

    def get_ipap_message(self, bidding_object: BiddingObject, auction: Auction,
                         template_container: IpapTemplateContainer, message: IpapMessage):

        if bidding_object.get_parent_key() != auction.get_key():
            raise ValueError("the auction is not the same as the one referenced in the bidding object")

        # Find both templates types for the bidding object.
        tempType = IpapTemplate.get_data_template(bidding_object.get_template_object_type())
        data_template_id = auction.get_bidding_object_template(bidding_object.get_template_object_type(), tempType)

        tempType = IpapTemplate.get_opts_template(bidding_object.get_template_object_type())
        option_template_id = auction.get_bidding_object_template(bidding_object.get_template_object_type(), tempType)

        # Insert BiddingObject's templates.
        data_template = template_container.get_template(data_template_id)
        message.make_template(data_template)

        option_template = template_container.get_template(option_template_id)
        message.make_template(option_template)

        # Include data records.
        for element_name in bidding_object.elements:
            config_params = bidding_object.elements[element_name]
            self.include_data_record(data_template, bidding_object, element_name, config_params, message)

        # Include option records.
        last_stop = datetime.now()
        for option_name in bidding_object.options:
            interval = bidding_object.calculate_interval(option_name, last_stop)
            config_params = bidding_object.options[option_name]
            self.include_options_record(option_template, bidding_object,
                                        option_name, interval.start, interval.stop, config_params, message)
            last_stop = interval.stop
