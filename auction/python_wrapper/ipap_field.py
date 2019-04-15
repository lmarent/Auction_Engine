from python_wrapper.ipap_value_field import IpapValueField
from ctypes import cdll
from ctypes import c_int
from ctypes import c_uint8
from ctypes import c_uint16
from ctypes import c_uint32
from ctypes import c_uint64
from ctypes import c_float
from ctypes import c_double
from ctypes import create_string_buffer
from ctypes import sizeof

from ctypes import c_size_t
from ctypes import c_char_p
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

    def get_ipap_field_value_uint8(self, value:int):
        obj = lib.ipap_field_get_ipap_value_field_uint8(self.obj, c_uint8(value))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_uint16(self, value:int):
        obj = lib.ipap_field_get_ipap_value_field_uint16(self.obj, c_uint16(value))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_uint32(self, value:int):
        obj = lib.ipap_field_get_ipap_value_field_uint32(self.obj, c_uint32(value))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_uint64(self, value:int):
        obj = lib.ipap_field_get_ipap_value_field_uint64(self.obj, c_uint64(value))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_float(self, value:float):
        obj = lib.ipap_field_get_ipap_value_field_float(self.obj, c_float(value))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_double(self, value:float):
        obj = lib.ipap_field_get_ipap_value_field_double(self.obj, c_double(value))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_string(self, value:str) -> IpapValueField:
        obj = lib.ipap_field_get_ipap_value_field_string(self.obj, c_char_p(value), c_int(len(value)))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_ipv6(self, value: str):
        obj = lib.ipap_field_get_ipap_value_field_ipv6(self.obj, c_char_p(value), c_int(len(value)))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def get_ipap_field_value_ipv4(self, value: str):
        obj = lib.ipap_field_get_ipap_value_field_ipv4(self.obj, c_char_p(value), c_int(len(value)))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be created')

    def num_characters(self, value: IpapValueField) -> int:
        num_characters = lib.ipap_field_number_characters
        num_characters.restype = c_int

        return lib.ipap_field_number_characters(self.obj, value.obj)


    # TODO: Create the function.
    # def get_ipap_field_value_ubytes(self, value:str):
    #     obj = lib.ipap_field_get_ipap_value_field_bytes(self.obj, c_char_p(value), c_int(len(value)))
    #
    #     if obj:  # not null
    #         field_value = IpapValueField(obj=obj)
    #         return field_value
    #     else:
    #         raise ValueError('Field value could not be created')

    def write_value(self, value: IpapValueField) -> str:
        write_value = lib.ipap_field_write_value
        write_value.restype = c_char_p

        num_characters = int(self.num_characters(value) + 1)
        result = create_string_buffer(num_characters)

        lib.ipap_field_write_value(self.obj, value.obj, result, sizeof(result))
        return result.value.decode('utf-8')

    def parse(self, value:str) -> IpapValueField:
        bvalue = value.encode('utf-8')
        obj = lib.ipap_field_parse(self.obj, c_char_p(bvalue))

        if obj:  # not null
            field_value = IpapValueField(obj=obj)
            return field_value
        else:
            raise ValueError('Field value could not be parsed')

    def __del__(self):
        if self.obj: # not null
            lib.ipap_field_destroy(self.obj)

    def destroy(self):
        lib.ipap_field_destroy(self.obj)

