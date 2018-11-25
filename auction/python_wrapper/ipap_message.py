from ctypes import cdll
from ctypes import c_ubyte
from ctypes import c_size_t
from ctypes import c_uint16
from ctypes import c_uint32
from ctypes import c_int
from ctypes import c_bool
from ctypes import pointer
from ctypes import POINTER
lib = cdll.LoadLibrary('libipap.so')

from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_data_record import IpapDataRecord

class IpapMessage:

    def __init__(self, domain_id : int, ipap_version : int, _encode_network : bool):
        self.obj = lib.ipap_message_new(c_int(domain_id), c_int(ipap_version), c_bool(_encode_network))

    # @classmethod
    # def from_message(cls, param : POINTER(c_ubyte), message_length : c_size_t, _decode_network : bool):
    #    return cls(lib.ipap_message_new_message(param, message_length, _decode_network))

    def close(self):
        lib.ipap_message_close(self.obj)

    def new_data_template(self, nfields : int, template_type_id : int) -> c_uint16:
        return lib.ipap_message_new_data_template(self.obj, c_int(nfields), c_int(template_type_id))

    def add_field(self, templid : int, eno : int, type : int):
        lib.ipap_message_add_field(self.obj, c_uint16(templid), c_uint32(eno), c_uint16(type))

    def delete_template(self, templid : int):
        lib.ipap_message_delete_template(self.obj, c_uint16(templid))

    def delete_all_templates(self):
        lib.ipap_message_delete_all_templates(self.obj)

    def get_template_list(self) -> list:
        size = lib.ipap_message_get_template_list_size(self.obj)
        list_return = []

        for i in range(0,size):
            templ_id = lib.ipap_message_get_template_at_pos(self.obj, c_int(i))

            if templ_id >=0: # not invalid
                list_return.append(templ_id)
            else:
                raise ValueError('Template at position {0} was not found'.format(str(i)))
        return list_return

    def get_template_object(self, templ_id : int) -> IpapTemplate:
        obj = lib.ipap_mesage_get_template_object(self.obj, c_uint16(templ_id))
        if obj: # not null
            template = IpapTemplate(obj)
            return template
        else:
            raise ValueError("Template with id:{} was not found".format(str(templ_id)))

    def get_data_record_size(self):
        return lib.ipap_message_get_data_record_size(self.obj)

    def get_data_record_at_pos(self, pos : int ):
        obj = lib.ipap_message_get_data_record_at_pos(self.obj, c_int(pos))
        if obj: # not null
            IpapDataRecord(obj=obj)
        else:
            raise ValueError("Data record at pos {0} was not found".format(str(int)) )