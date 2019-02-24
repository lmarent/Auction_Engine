from python_wrapper.ipap_template import ObjectType
from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_template_container import IpapTemplateContainer

from foundation.ipap_message_parser import IpapMessageParser
from foundation.bidding_object import BiddingObject


class IpapBiddingObjectParser(IpapMessageParser):

    def __init__(self, domain):
        super(IpapBiddingObjectParser, self).__init__(domain)


    def parse_bidding_object(self, templates: list, data_records: list,
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

        data_template, opts_template = self.insert_auction_templates( templates, ipap_template_container)

        # Read data records
        for data_record in data_records:
            template_id = data_record.get_template_id()
            # Read a data record for a data template
            if template_id == data_template.get_template_id():
                data_misc = self.read_record(data_template, data_record)
                bidding_object_key = self.extract_param('biddingobjectid', data_misc)
                auction_key = self.extract_param('auctionid', data_misc)
                auction_status = self.extract_param('status', data_misc)
                resource_key = self.extract_param('resourceid', data_misc)
                bidding_object_type = self.extract_param('biddingobjecttype', data_misc)
                nbr_data_read = nbr_data_read + 1

            if template_id == opts_template.get_template_id():
                opts_misc = self.read_record(opts_template, data_record)
                action_name = self.extract_param('algoritmname', data_misc)
                nbr_option_read = nbr_option_read + 1

        if nbr_data_read == 0:
            raise ValueError("A data template was not given")

        if nbr_option_read == 0:
            raise ValueError("An option template was not given")

        action = BiddingObject(action_name.value, True, opts_misc)
        auction = Auction(auction_key.value, resource_key.value, action, data_misc )
        auction.set_state(AuctioningObjectState(ParseFormats.parse_int(auction_status.value)))
        self.build_associated_templates(templates, auction, ipap_template_container)

        template_ids = template_list.value.split(',')

        for template_sid in template_ids:
            template = ipap_template_container.get_template(ParseFormats.parse_int(template_sid))

            auction.set_bidding_object_template(template.get_object_type(template.get_type()),
                                                template.get_type(), template.get_template_id())

        return auction



    def parse(self, ipap_message: IpapMessage, ipap_template_container: IpapTemplateContainer):

        bidding_object_ret = []

        # Splits the message by object.
        object_templates, object_data_records, templates_not_related = self.split(ipap_message)

        # loop through data records and parse the auction data
        for object_key in object_data_records:
            if object_key.get_key() in [ ObjectType.IPAP_BID, ObjectType.IPAP_ALLOCATION ]:
                bidding_object = self.parse_bidding_object(object_key, object_templates[object_key], object_data_records[object_key])
                bidding_object_ret.append(bidding_object)

        return bidding_object_ret
