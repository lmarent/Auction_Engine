from foundation.ipap_message_parser import IpapMessageParser
from foundation.ipap_message_parser import IpapObjectKey
from foundation.allocation import Allocation
from foundation.auction_manager import AuctionManager
from foundation.interval import Interval
from foundation.auctioning_object import AuctioningObjectState
from foundation.parse_format import ParseFormats

from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_template_container import IpapTemplateContainer
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_template import ObjectType

from datetime import datetime


class IpapAllocationParser(IpapMessageParser):

    def __init__(self, domain: int):
        super(IpapAllocationParser, self).__init__(domain)

    @staticmethod
    def convert_options_interval(opts: list) -> list:
        """
        Gets the options read from the message and creates intervals representing them.

        :param opts: list of config params
        :return: intervals.
        """
        intervals = []

        for opts_misc in opts:
            config_dict = {}
            for config_param in opts_misc:
                config_dict[config_param.name] = config_param.value

            interval = Interval()
            interval.parse_interval(config_dict, datetime.now())
            intervals.append(interval)

        return intervals

    def parse_allocation(self, object_key: IpapObjectKey, templates: list, data_records: list,
                         ipap_template_container: IpapTemplateContainer) -> Allocation:
        """
        Parse an allocation object from the ipap_message

        :param object_key: object key for the allocation that is going to be parsed.
        :param templates: templates for the allocation
        :param data_records: records for the allocation
        :param ipap_template_container: template container where we have to include the templates.
        :return: allocation object parsed.
        """
        nbr_data_read = 0
        nbr_option_read = 0
        bidding_object_key = None
        allocation_key = None
        auction_key = None
        status = None
        data_misc = {}

        data_template, opts_template = self.insert_auction_templates(object_key.get_object_type(),
                                                                     templates, ipap_template_container)

        opts = []
        # Read data records
        for data_record in data_records:
            template_id = data_record.get_template_id()
            # Read a data record for a data template
            if template_id == data_template.get_template_id():
                data_misc = self.read_record(data_template, data_record)
                bidding_object_key = self.extract_param(data_misc, 'biddingobjectid').value
                auction_key = self.extract_param(data_misc, 'auctionid').value
                allocation_key = self.extract_param(data_misc, 'allocationid').value
                status = self.extract_param(data_misc, 'status').value
                nbr_data_read = nbr_data_read + 1

            if template_id == opts_template.get_template_id():
                opts_misc = self.read_record(opts_template, data_record)
                opts.append(opts_misc)
                nbr_option_read = nbr_option_read + 1

        if nbr_data_read == 0:
            raise ValueError("A data template was not given")

        if nbr_option_read == 0:
            raise ValueError("An option template was not given")

        intervals = self.convert_options_interval(opts)

        allocation = Allocation(auction_key, bidding_object_key, allocation_key, data_misc, intervals)
        allocation.set_state(AuctioningObjectState(ParseFormats.parse_int(status.value)))

        return allocation

    def parse(self, ipap_message: IpapMessage, ipap_template_container: IpapTemplateContainer) -> list:

        allocation_ret = []

        # Splits the message by object.
        object_templates, object_data_records, templates_not_related = self.split(ipap_message)

        # loop through data records and parse the auction data
        for object_key in object_data_records:
            if object_key.get_object_type() == ObjectType.IPAP_ALLOCATION:
                allocation = self.parse_allocation(object_key, object_templates[object_key],
                                                   object_data_records[object_key], ipap_template_container)
                allocation_ret.append(allocation)

        return allocation_ret

    def include_data_record(self, template: IpapTemplate, allocation: Allocation, record_id: str,
                            config_params: dict, message: IpapMessage):

        ipap_data_record = IpapDataRecord(obj=None, templ_id=template.get_template_id())

        # Insert the auction id field.
        self.insert_string_field('auctionid', allocation.get_auction_key(), ipap_data_record)

        # Insert the bidding object id field.
        self.insert_string_field('biddingobjectid', allocation.get_bid_key(), ipap_data_record)

        # Insert the allocation id field.
        self.insert_string_field('allocationid', allocation.get_key(), ipap_data_record)

        # Add the Record Id
        self.insert_string_field('recordid', record_id, ipap_data_record)

        # Add the Status
        self.insert_integer_field('status', allocation.get_state().value, ipap_data_record)

        # Add bidding_object type
        self.insert_integer_field('biddingobjecttype', allocation.get_type().value, ipap_data_record)

        # Adds non mandatory fields.
        mandatory_fields = template.get_template_type_mandatory_field(template.get_type())
        self.include_non_mandatory_fields(mandatory_fields, config_params, ipap_data_record)

        # Include the data record in the message.
        message.include_data(template.get_template_id(), ipap_data_record)

    def include_options_record(self, template: IpapTemplate, allocation: Allocation, record_id: str,
                               start: datetime, stop: datetime, message: IpapMessage):

        ipap_record = IpapDataRecord(obj=None, templ_id=template.get_template_id())

        # Insert the auction id field.
        self.insert_string_field('auctionid', allocation.get_auction_key(), ipap_record)

        # Insert the bidding object id field.
        self.insert_string_field('biddingobjectid', allocation.get_bid_key(), ipap_record)

        # Insert the allocation id field.
        self.insert_string_field('allocationid', allocation.get_key(), ipap_record)

        # Add the Record Id
        self.insert_string_field('recordid', record_id, ipap_record)

        # Add the start time - Unix time is seconds from 1970-1-1 .
        self.insert_datetime_field('start', start, ipap_record)

        # Add the end time.
        self.insert_datetime_field('stop', stop, ipap_record)

        message.include_data(template.get_template_id(), ipap_record)

    def get_ipap_message(self, allocation: Allocation, template_container: IpapTemplateContainer) -> IpapMessage:
        """

        :return:
        """
        message = IpapMessage(self.domain, IpapMessage.IPAP_VERSION, True)

        auction_manager = AuctionManager(self.domain)
        auction = auction_manager.get_auction(allocation.get_auction_key())

        # Find both templates types for the bidding object.
        temp_type = IpapTemplate.get_data_template(allocation.get_template_object_type())
        data_template_id = auction.get_bidding_object_template(allocation.get_template_object_type(), temp_type)

        temp_type = IpapTemplate.get_opts_template(allocation.get_template_object_type())
        option_template_id = auction.get_bidding_object_template(allocation.get_template_object_type(), temp_type)

        # Insert allocations's templates.a
        data_template = template_container.get_template(data_template_id)
        message.make_template(data_template)

        option_template = template_container.get_template(option_template_id)
        message.make_template(option_template)

        # Include data records.
        self.include_data_record(data_template, allocation, 'Record_1', allocation.config_params, message)

        # Include option records.
        index = 1
        for interval in allocation.intervals:
            record_id = 'Record_{0}'.format(str(index))
            self.include_options_record(option_template, allocation,
                                        record_id, interval.start, interval.stop, message)
            index = index + 1

        return message
