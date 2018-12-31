from ctypes import cdll
from ctypes import c_int
from ctypes import c_uint8
from ctypes import c_uint16
from ctypes import c_uint32
from ctypes import c_uint64
from ctypes import c_float
from ctypes import c_double
from ctypes import POINTER
from ctypes import c_size_t
from ctypes import c_char_p
from ctypes import c_wchar_p
from ctypes import pointer
lib = cdll.LoadLibrary('libipap.so')

class IpapValueField:

    def __init__(self, obj=None):
        if obj:
            self.obj = obj
        else:
            self.obj = lib.ipap_value_field_new()

    def set_value_uint8(self, value : int):
        lib.ipap_value_field_set_value_int8(self.obj, c_uint8(value))

    def set_value_uint16(self, value :int):
        lib.ipap_value_field_set_value_int16(self.obj, c_uint16(value))

    def set_value_uint32(self, value:int):
        lib.ipap_value_field_set_value_int32(self.obj, c_uint32(value))

    def set_value_uint64(self, value:int):
        lib.ipap_value_field_set_value_int64(self.obj, c_uint64(value))

    def set_value_float32(self, value):
        lib.ipap_value_field_set_value_float32(self.obj, c_float(value))

    def set_value_double(self, value):
        lib.ipap_value_field_set_value_float64(self.obj, c_double(value))

    def set_value_vchar(self, value, lenght : int):
        lib.ipap_value_field_set_value_vchar(self.obj, c_char_p(value), c_int(lenght))

    def get_value_uint8(self):
        return lib.ipap_value_field_get_value_int8(self.obj)

    def get_value_uint16(self):
        return lib.ipap_value_field_get_value_int16(self.obj)

    def get_value_uint32(self):
        return lib.ipap_value_field_get_value_int32(self.obj)

    def get_value_uint64(self):
        return lib.ipap_value_field_get_value_int64(self.obj)

    def get_value_float(self):
        get_value_float = lib.ipap_value_field_get_value_float
        get_value_float.restype = c_float

        value = lib.ipap_value_field_get_value_float(self.obj)
        return value

    def get_value_double(self):
        get_value_double = lib.ipap_value_field_get_value_double
        get_value_double.restype = c_double

        value = lib.ipap_value_field_get_value_double(self.obj)
        return value

    def get_value_vchar(self):
        get_value_vchar = lib.ipap_value_field_get_value_vchar
        get_value_vchar.restype = c_char_p

        # we restrict to length to remove the ending null character.
        lenght = lib.ipap_value_field_get_length(self.obj)
        value =  lib.ipap_value_field_get_value_vchar(self.obj)
        return value[:lenght]

    def get_lenght(self):
        return lib.ipap_value_field_get_length(self.obj)
