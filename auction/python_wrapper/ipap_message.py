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

    def add_field(self, templid : c_uint16, eno : c_uint32, type : c_uint16):
        lib.ipap_message_add_field(self.obj, templid, eno, type)

    def delete_template(self, templid : c_uint16):
        lib.ipap_message_delete_template(self.obj, templid)

    def delete_all_templates(self):
        lib.ipap_message_delete_all_templates(self.obj)

    def get_template_list(self) -> list:
        return lib.ipap_message_get_template_list(self.obj)

    def get_template_object(self, templid : int):
        return lib.ipap_mesage_get_template_object(self.obj, c_uint16(templid))