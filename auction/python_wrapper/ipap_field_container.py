from python_wrapper.ipap_field import  IpapField
from ctypes import cdll
from ctypes import c_int
lib = cdll.LoadLibrary('libipap.so')


class IpApFieldContainer:

    def __init__(self):
        self.obj = lib.ipap_field_container_new()

    def initialize_forward(self):
        lib.ipap_field_container_initialize_forward(self.obj)

    def initialize_reverse(self):
        lib.ipap_field_container_initialize_reverse(self.obj)

    def get_field(self, eno :int, type: int):
        field = IpapField()
        field.destroy()
        obj = lib.ipap_field_container_get_field_pointer(self.obj, c_int(eno), c_int(type))

        if obj: # not null
            field.obj = obj
        else:
            raise ValueError('Field not found')

        return field