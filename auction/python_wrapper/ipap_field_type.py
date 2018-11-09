from ctypes import c_size_t
from ctypes import c_int
from ctypes import c_double
from ctypes import c_char_p
from ctypes import cdll
from ctypes import Structure
lib = cdll.LoadLibrary('libipap.so')


class IpapFieldType(Structure):
    """
    Creates an structure to match ipap_field_type_t
    """
    _fields_ = [('eno', c_int),
                ('ftype', c_int),
                ('length', c_size_t),
                ('coding', c_int),
                ('name', c_char_p),
                ('xml_name',c_char_p),
                ('documentation', c_char_p)
                ]
