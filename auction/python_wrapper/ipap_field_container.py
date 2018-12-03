from python_wrapper.ipap_field import  IpapField
from ctypes import cdll
from ctypes import c_int
lib = cdll.LoadLibrary('libipap.so')


class IpapFieldContainer:

    def __init__(self):
        self.obj = lib.ipap_field_container_new()

    def initialize_forward(self):
        lib.ipap_field_container_initialize_forward(self.obj)

    def initialize_reverse(self):
        lib.ipap_field_container_initialize_reverse(self.obj)

    def get_field(self, eno: int, type: int):
        obj = lib.ipap_field_container_get_field_pointer(self.obj, c_int(eno), c_int(type))

        if obj: # not null
            field = IpapField(obj)
            return field
        else:
            raise ValueError('Field {0}.{1} not found'.format(str(eno),str(type)))


