from python_wrapper.ipap_field_type import  IpapFieldType
from ctypes import cdll
from ctypes import c_int
from ctypes import c_size_t
from ctypes import c_char_p
from ctypes import c_wchar_p
from ctypes import pointer
lib = cdll.LoadLibrary('libipap.so')


class IpapField:

    def __init__(self, obj=None):
        if obj:
            self.obj = obj
        else:
            self.obj = lib.ipap_field_new()

    def set_field_type(self, eno :int, ftype : int, lenght : int,  coding : int,
                       name :str, xml_name : str, documentation : str):
        lib.ipap_field_set_field_type(self.obj, c_int(eno), c_int(ftype), c_size_t(lenght),
                                      c_int(coding), c_char_p(name), c_char_p(xml_name), c_char_p(documentation)
                                      )

    def get_eno(self) -> int:
        return lib.ipap_field_get_eno(self.obj)

    def get_type(self) -> int:
        return lib.ipap_field_get_type(self.obj)

    def get_length(self):
        return lib.ipap_field_get_length(self.obj)

    def get_field_name(self):
        get_field_name = lib.ipap_field_get_field_name
        get_field_name.restype = c_char_p

        return lib.ipap_field_get_field_name(self.obj)

    def get_xml_name(self):
        get_xml_name = lib.ipap_field_get_xml_name
        get_xml_name.restype = c_char_p

        return lib.ipap_field_get_xml_name(self.obj)

    def get_documentation(self):
        get_documentation = lib.ipap_field_get_documentation
        get_documentation.restype = c_char_p

        return lib.ipap_field_get_documentation(self.obj)

    def __del__(self):
        if self.obj: # not null
            lib.ipap_field_destroy(self.obj)

    def destroy(self):
        lib.ipap_field_destroy(self.obj)

