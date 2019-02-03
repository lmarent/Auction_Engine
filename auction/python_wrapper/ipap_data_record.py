from ctypes import cdll
from ctypes import c_uint16
from ctypes import c_int

from python_wrapper.ipap_value_field import IpapValueField
from python_wrapper.ipap_field_key import IpapFieldKey

lib = cdll.LoadLibrary('libipap.so')


class IpapDataRecord:

    def __init__(self, obj=None, templ_id=0):
        if obj:
            self.obj = obj
        else:
            self.obj = lib.ipap_data_record_new(c_uint16(templ_id))

    def get_template_id(self) -> int:
        return lib.ipap_data_record_get_template_id(self.obj)

    def insert_field(self, eno: int, ftype: int, field_value: IpapValueField):
        lib.ipap_data_record_insert_field(self.obj, c_int(eno), c_int(ftype), field_value.obj)

    def get_num_fields(self) -> int:
        return lib.ipap_data_record_get_num_fields(self.obj)

    def get_field_at_pos(self, pos: int) -> IpapFieldKey:
        obj = lib.ipap_data_record_get_field_at_pos(self.obj, c_int(pos))
        if obj:
            value = IpapFieldKey(obj=obj)
            return value
        else:
            raise ValueError("Field at pos {0} was not found in data record".format(str(pos)))

    def get_field(self, eno: int, ftype: int) -> IpapValueField:
        obj = lib.ipap_data_record_get_field(self.obj, c_int(eno), c_int(ftype))
        if obj:
            value = IpapValueField(obj=obj)
            return value
        else:
            raise ValueError("Field {0}.{1} given was not found in data record".format(str(eno), str(ftype)))

    def get_field_length(self, eno: int, ftype: int):
        return lib.ipap_data_record_get_length(self.obj, c_int(eno), c_int(ftype))

    def clear(self):
        lib.ipap_data_record_clear(self.obj)

    def __del__(self):
        if self.obj:
            lib.ipap_data_record_destroy(self.obj)
