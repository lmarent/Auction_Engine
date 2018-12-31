from datetime import datetime

from auction_client.resource_request import ResourceRequest

from foundation.ipap_message_parser import IpapMessageParser
from foundation.field_def_manager import FieldDefManager
from foundation.interval import Interval

from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_field import IpapField
from python_wrapper.ipap_field_container import IpapFieldContainer

class IpapResourceRequestParser(IpapMessageParser):


    def __init__(self, domain:int):
        super(IpapResourceRequestParser, self).__init__(domain=domain)

    @staticmethod
    def _add_fields_option_template(message:IpapMessage) -> int:
        """
        Adds required field for the bid's option template
        :return: template id created for the message.
        """
        template = IpapTemplate()
        field_list = template.get_template_type_mandatory_field(TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE)
        template_id = self.message.new_data_template(len(field_list), TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE)

        for field in field_list:
            message.add_field(template_id, field.get_eno(), field.get_ftype())

        return template_id

    @staticmethod
    def _add_option_record(record_id: str, resource_id:str, interval: Interval, use_ipv6:bool,
                           ip_address4: str, ip_address6:str, port:int, template_id: int, message: IpapMessage):
        """
        Adds the field of all auction relationship into option message's template
        :return:
        """
        data_option = IpapDataRecord(templ_id=template_id)

        field_def_manager = FieldDefManager()

        ipap_field_container = IpapFieldContainer()
        ipap_field_container.initialize_forward()
        ipap_field_container.initialize_reverse()

        # Add the Resource Id
        resource_id = field_def_manager.get_field('resourceid')
        resource_field:IpapField = ipap_field_container.get_field(int(resource_id['eno']), int(resource_id['ftype']))
        data_option.insert_field(int(resource_id['eno']), int(resource_id['ftype']),
                                 resource_field.get_ipap_field_value_string(record_id))

        # Add the start datetime
        start = field_def_manager.get_field('start')
        start_field = ipap_field_container.get_field(int(start['eno']), int(start['ftype']))
        seconds = (interval.start - datetime.fromtimestamp(0)).total_seconds()
        data_option.insert_field(int(start['eno']), int(start['ftype']),
                                 start_field.get_ipap_field_value_uint64(seconds))

        # Add the endtime
        stop = field_def_manager.get_field('stop')
        stop_field = ipap_field_container.get_field(int(stop['eno']), int(stop['ftype']))
        seconds = (interval.stop - datetime.fromtimestamp(0)).total_seconds()
        data_option.insert_field(int(stop['eno']), int(stop['ftype']),
                                 stop_field.get_ipap_field_value_uint64(seconds))

        # Add the interval.
        interval_def = field_def_manager.get_field('interval')
        interval_field = ipap_field_container.get_field(int(interval_def['eno']), int(interval_def['ftype']))
        data_option.insert_field(int(interval_def['eno']), int(interval_def['ftype']),
                                 interval_field.get_ipap_field_value_uint64(interval.interval))

        # Add the IPversion
        ip_version = field_def_manager.get_field('ipversion')
        ip_version_field = ipap_field_container.get_field(int(ip_version['eno']), int(ip_version['ftype']))
        if use_ipv6:
            data_option.insert_field(int(ip_version['eno']), int(ip_version['ftype']),
                                     ip_version_field.get_ipap_field_value_uint8(6))
        else:
            data_option.insert_field(int(ip_version['eno']), int(ip_version['ftype']),
                                     ip_version_field.get_ipap_field_value_uint8(4))

        # Add the Ipv6 Address value
        scr_ipv6 = field_def_manager.get_field('srcipv6')
        scr_ipv6_field = ipap_field_container.get_field(int(scr_ipv6['eno']), int(scr_ipv6['ftype']))
        if use_ipv6:
            data_option.insert_field(int(scr_ipv6['eno']), int(scr_ipv6['ftype']),
                                     scr_ipv6_field.get_ipap_field_value_ipv6(ip_address6))
        else:
            data_option.insert_field(int(scr_ipv6['eno']), int(scr_ipv6['ftype']),
                                     scr_ipv6_field.get_ipap_field_value_ipv6("0:0:0:0:0:0:0:0"))

        # Add the Ipv4 Address value
        scr_ipv4 = field_def_manager.get_field('srcip')
        scr_ipv4_field = ipap_field_container.get_field(int(scr_ipv4['eno']), int(scr_ipv4['ftype']))
        if use_ipv6:
            data_option.insert_field(int(scr_ipv4['eno']), int(scr_ipv4['ftype']),
                                     scr_ipv4_field.get_ipap_field_value_ipv4("0.0.0.0"))
        else:
            data_option.insert_field(int(scr_ipv4['eno']), int(scr_ipv4['ftype']),
                                     scr_ipv4_field.get_ipap_field_value_ipv4(ip_address4))

        # Add the destination port
        scr_port = field_def_manager.get_field('srcport')
        scr_port_field = ipap_field_container.get_field(int(scr_port['eno']), int(scr_port['ftype']))
        data_option.insert_field(int(scr_port['eno']), int(scr_port['ftype']),
                                 scr_port_field.get_ipap_field_value_uint16(port))

        message.include_data(template_id, data_option)

    def get_ipap_message(self, start: datetime, resource_request: ResourceRequest, resource_id:str, use_ipv6:bool,
                           ip_address4: str, ip_address6:str, port:int) -> IpapMessage:
        """
        gets the ipap_message that represents an specifc resource request.
        :return:
        """

        message = IpapMessage(domain_id=self.domain, ipap_version=0, _encode_network=True)
        interval = resource_request.get_interval_by_start_time(start)
        template_id = self._add_fields_option_template(message)

        # Build the recordId as the resourceRequestSet + resourceRequestName
        record_id = resource_request.get_ipap_id(self.domain)

        self._add_option_record(record_id, resource_id, interval, use_ipv6, ip_address4,
                                ip_address6, port, template_id, message)

        # fill the char buffer to send
        message.output()

        return self.message

