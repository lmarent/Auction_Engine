from datetime import datetime

from auction_client.resource_request import ResourceRequest

from foundation.ipap_message_parser import IpapMessageParser
from foundation.interval import Interval

from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_data_record import IpapDataRecord


class IpapResourceRequestParser(IpapMessageParser):

    def __init__(self, domain: int):
        super(IpapResourceRequestParser, self).__init__(domain=domain)

    @staticmethod
    def _add_fields_option_template(message: IpapMessage) -> int:
        """
        Adds required field for the bid's option template
        :return: template id created for the message.
        """
        template = IpapTemplate()
        field_list = template.get_template_type_mandatory_field(TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE)
        template_id = message.new_data_template(len(field_list), TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE)

        for field in field_list:
            message.add_field(template_id, field.get_eno(), field.get_ftype())

        return template_id

    def _add_option_record(self, record_id: str, resource_id: str, interval: Interval, use_ipv6: bool,
                           ip_address4: str, ip_address6: str, port: int, template_id: int, message: IpapMessage):
        """
        Adds the field of all auction relationship into option message's template
        :return:
        """
        data_option = IpapDataRecord(templ_id=template_id)

        # Add the record Id
        self.insert_string_field('recordid', record_id, data_option)

        # Add the Resource Id
        self.insert_string_field('resourceid', resource_id, data_option)

        # Add the start datetime
        self.insert_datetime_field('start', interval.start, data_option)

        # Add the endtime
        self.insert_datetime_field('stop', interval.stop, data_option)

        # Add the interval.
        self.insert_integer_field('interval', interval.interval, data_option)

        # Add the IPversion
        if use_ipv6:
            self.insert_integer_field('ipversion', 6, data_option)
        else:
            self.insert_integer_field('ipversion', 4, data_option)

        # Add the Ipv6 Address value
        if use_ipv6:
            self.insert_ipv6_field('srcipv6', ip_address6, data_option)
        else:
            self.insert_ipv4_field('srcipv6', '0:0:0:0:0:0:0:0', data_option)

        # Add the Ipv4 Address value
        if use_ipv6:
            self.insert_ipv4_field('srcipv4', '0.0.0.0', data_option)
        else:
            self.insert_ipv4_field('srcipv4', ip_address4, data_option)

        # Add the destination port
        self.insert_integer_field('srcport', port, data_option)

        message.include_data(template_id, data_option)

    def get_ipap_message(self, start: datetime, resource_request: ResourceRequest, resource_id: str, use_ipv6: bool,
                         ip_address4: str, ip_address6: str, port: int) -> IpapMessage:
        """
        gets the ipap_message that represents an specifc resource request.
        :return:
        """

        message = IpapMessage(domain_id=self.domain, ipap_version=IpapMessage.IPAP_VERSION, _encode_network=True)
        interval = resource_request.get_interval_by_start_time(start)
        template_id = self._add_fields_option_template(message)

        if template_id < 0:
            self.logger.error("error creating the template")
            return None

        # Build the recordId as the resourceRequestSet + resourceRequestName
        record_id = resource_request.get_key()

        self._add_option_record(record_id, resource_id, interval, use_ipv6, ip_address4,
                                ip_address6, port, template_id, message)

        # fill the char buffer to send
        message.output()

        return message
