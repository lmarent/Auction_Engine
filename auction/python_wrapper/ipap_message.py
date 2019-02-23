from ctypes import cdll
from ctypes import c_uint16
from ctypes import c_uint32
from ctypes import c_int
from ctypes import c_bool
from ctypes import POINTER
from ctypes import c_ubyte

from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_data_record import IpapDataRecord

lib = cdll.LoadLibrary('libipap.so')


class IpapMessageType:
    """
    This class maintains the type of information within the message.
    """

    def __init__(self):
        self.ask_message = False
        self.auction_message = False
        self.bidding_object_message = False
        self.allocation_message = False

    def set_ask_message(self, ask_message: bool):
        self.ask_message = ask_message

    def is_ask_message(self) -> bool:
        return self.ask_message

    def set_auction_message(self, auction_message: bool):
        self.auction_message = auction_message

    def is_auction_message(self) -> bool:
        return self.auction_message

    def is_bidding_message(self) -> bool:
        return self.bidding_object_message

    def set_bidding_message(self, bidding_message: bool):
        self.bidding_object_message = bidding_message

    def is_allocation_message(self) -> bool:
        return self.allocation_message

    def set_allocation_message(self, allocation_message: bool):
        self.allocation_message = allocation_message


class IpapMessage:
    IPAP_VERSION = 0x01

    def __init__(self, domain_id: int, ipap_version: int, _encode_network: bool, value: str = None):
        if value:
            array_unsigned_char = c_ubyte * len(value)
            mes = array_unsigned_char()
            for i in range(0, len(value)):
                mes[i] = ord(value[i])

            obj = lib.ipap_message_new_message(mes, c_int(len(value)), c_bool(_encode_network))
            if obj:
                self.obj = obj
            else:
                raise ValueError("Not a Ipap Message")
        else:
            self.obj = lib.ipap_message_new(c_int(domain_id), c_int(ipap_version), c_bool(_encode_network))

    def new_data_template(self, nfields: int, template_type_id: TemplateType) -> c_uint16:
        return lib.ipap_message_new_data_template(self.obj, c_int(nfields), c_int(template_type_id.value))

    def add_field(self, templid: int, eno: int, type: int):
        val = lib.ipap_message_add_field(self.obj, c_uint16(templid), c_uint32(eno), c_uint16(type))
        if val < 0:
            raise ValueError("Invalid argument. The field was not included")

    def delete_template(self, templid: int):
        lib.ipap_message_delete_template(self.obj, c_uint16(templid))

    def delete_all_templates(self):
        lib.ipap_message_delete_all_templates(self.obj)

    def get_template_list(self) -> list:
        size = lib.ipap_message_get_template_list_size(self.obj)
        list_return = []

        for i in range(0, size):
            templ_id = lib.ipap_message_get_template_at_pos(self.obj, c_int(i))

            if templ_id >= 0:  # not invalid
                list_return.append(templ_id)
            else:
                raise ValueError('Template at position {0} was not found'.format(str(i)))
        return list_return

    def get_template_object(self, templ_id: int) -> IpapTemplate:
        obj = lib.ipap_message_get_template_object(self.obj, c_uint16(templ_id))
        if obj:  # not null
            template = IpapTemplate(obj)
            return template
        else:
            raise ValueError("Template with id:{} was not found".format(str(templ_id)))

    def include_data(self, template_id: int, ipap_data_record: IpapDataRecord):
        return lib.ipap_message_include_data(self.obj, c_uint16(template_id), ipap_data_record.obj)

    def get_data_record_size(self):
        return lib.ipap_message_get_data_record_size(self.obj)

    def get_data_record_at_pos(self, pos: int) -> IpapDataRecord:
        obj = lib.ipap_message_get_data_record_at_pos(self.obj, c_int(pos))
        if obj:  # not null
            return IpapDataRecord(obj=obj)
        else:
            raise ValueError("Data record at pos {0} was not found".format(str(int)))

    def set_syn(self, syn: bool):
        lib.ipap_message_set_syn(self.obj, c_bool(syn))

    def get_syn(self) -> bool:
        return lib.ipap_message_get_syn(self.obj)

    def set_ack(self, ack: bool):
        lib.ipap_message_set_ack(self.obj, c_bool(ack))

    def get_ack(self) -> bool:
        return lib.ipap_message_get_ack(self.obj)

    def set_fin(self, fin: bool):
        lib.ipap_message_set_fin(self.obj, c_bool(fin))

    def get_fin(self):
        return lib.ipap_message_get_fin(self.obj)

    def get_seqno(self) -> int:
        get_value_uint32 = lib.ipap_message_get_seqno
        get_value_uint32.restype = c_uint32

        return lib.ipap_message_get_seqno(self.obj)

    def set_seqno(self, seq_no: int):
        lib.ipap_message_set_seqno(self.obj, c_uint32(seq_no))

    def get_ackseqno(self) -> int:
        get_value_uint32 = lib.ipap_message_get_ackseqno
        get_value_uint32.restype = c_uint32

        return lib.ipap_message_get_ackseqno(self.obj)

    def set_ack_seq_no(self, ack_seq_no: int):
        lib.ipap_message_set_ackseqno(self.obj, c_uint32(ack_seq_no))

    def output(self):
        lib.ipap_message_output(self.obj)

    def get_message(self) -> str:
        get_value_vchar = lib.ipap_message_get_message
        get_value_vchar.restype = POINTER(c_ubyte)

        # we restrict to length to remove the ending null character.
        # Here we make sure that the message is the buffers.
        lib.ipap_message_output(self.obj)

        lenght = lib.ipap_message_get_message_length(self.obj)
        value = lib.ipap_message_get_message(self.obj)

        ret_lst = [chr(value[x]) for x in range(0, lenght)]
        ret = ''.join(ret_lst)
        return ret

    def get_domain(self)-> int:
        return lib.ipap_message_get_domain(self.obj)

    def make_template(self, template: IpapTemplate):
        lib.ipap_message_make_template(self.obj, template.obj)

    def get_types(self) -> IpapMessageType:

        ipap_message_type = IpapMessageType()
        templates = self.get_template_list()
        for template_id in templates:
            template = self.get_template_object(template_id)
            if template.get_type() in [TemplateType.IPAP_SETID_ASK_OBJECT_TEMPLATE,
                                       TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE]:
                ipap_message_type.set_ask_message(True)

            if template.get_type() in [TemplateType.IPAP_SETID_AUCTION_TEMPLATE,
                                       TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE]:
                ipap_message_type.set_auction_message(True)

            if template.get_type() in [TemplateType.IPAP_SETID_BID_OBJECT_TEMPLATE,
                                       TemplateType.IPAP_OPTNS_BID_OBJECT_TEMPLATE]:
                ipap_message_type.set_bidding_message(True)

            if template.get_type() in [TemplateType.IPAP_SETID_ALLOC_OBJECT_TEMPLATE,
                                       TemplateType.IPAP_OPTNS_ALLOC_OBJECT_TEMPLATE]:
                ipap_message_type.set_allocation_message(True)
        return ipap_message_type

    def __del__(self):
        if self.obj:
            lib.ipap_message_destroy(self.obj)
