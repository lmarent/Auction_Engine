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
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_data_record import IpapDataRecord

class IpapMessage:

    def __init__(self, domain_id : int, ipap_version : int, _encode_network : bool):
        self.obj = lib.ipap_message_new(c_int(domain_id), c_int(ipap_version), c_bool(_encode_network))

    def new_data_template(self, nfields : int, template_type_id : TemplateType) -> c_uint16:
        return lib.ipap_message_new_data_template(self.obj, c_int(nfields), c_int(template_type_id.value))

    def add_field(self, templid : int, eno : int, type : int):
        val = lib.ipap_message_add_field(self.obj, c_uint16(templid), c_uint32(eno), c_uint16(type))
        if val < 0:
            raise ValueError("Invalid argument. The field was not included")

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

    def get_template_object(self, templ_id: int) -> IpapTemplate:
        obj = lib.ipap_message_get_template_object(self.obj, c_uint16(templ_id))
        if obj: # not null
            template = IpapTemplate(obj)
            return template
        else:
            raise ValueError("Template with id:{} was not found".format(str(templ_id)))

    def include_data(self, template_id: int, ipap_data_record : IpapDataRecord):
        lib.ipap_message_include_data(self.obj, template_id, ipap_data_record.obj)

    def get_data_record_size(self):
        return lib.ipap_message_get_data_record_size(self.obj)

    def get_data_record_at_pos(self, pos : int ) -> IpapDataRecord:
        obj = lib.ipap_message_get_data_record_at_pos(self.obj, c_int(pos))
        if obj: # not null
            return IpapDataRecord(obj=obj)
        else:
            raise ValueError("Data record at pos {0} was not found".format(str(int)) )

    def __del__(self):
        if self.obj:
            lib.ipap_message_destroy(self.obj)
