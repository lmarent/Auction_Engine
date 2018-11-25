from ctypes import cdll
from ctypes import c_uint16
from ctypes import c_int

from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_value_field import IpapValueField


lib = cdll.LoadLibrary('libipap.so')

class IpapDataRecord:

    def __init__(self, obj=None, templ_id=0 ):

        if obj:
            self.obj = obj
        else:
            self.lib.ipap_data_record_new(c_uint16(templ_id))

    def get_template_id(self):
        return lib.ipap_data_record_get_template_id(self.obj)

    def insert_field(self, eno : int, ftype: int, field_value : IpapFieldKey):
        lib.ipap_data_record_insert_field(self.obj, c_int(eno), c_int(ftype), field_value.obj)

    def get_num_fields(self) -> int:
        return lib.ipap_data_record_get_num_fields(self.obj)

    def get_field(self, eno : int , ftype : int ):
        obj = lib.ipap_data_record_get_num_fields(self.obj, c_int(eno), c_int(ftype))
        if obj:
            value = IpapValueField(obj)
        else:
            raise ValueError("Field {0}.{1} given was not found in data record".format(str(eno), str(ftype) ))

    def get_field_lenght(self, eno : int , ftype : int):
        return lib.ipap_data_record_get_length(self.obj, c_int(eno), c_int(ftype))

    def clear(self):
        lib.ipap_data_record_clear(self.obj)