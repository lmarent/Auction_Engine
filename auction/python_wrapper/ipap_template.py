from ctypes import cdll
from ctypes import c_int
from ctypes import c_uint16
from ctypes import c_uint8
from ctypes import POINTER
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_field import IpapField

lib = cdll.LoadLibrary('libipap.so')


( IPAP_SETID_AUCTION_TEMPLATE,
  IPAP_OPTNS_AUCTION_TEMPLATE,
  IPAP_SETID_BID_OBJECT_TEMPLATE,
  IPAP_OPTNS_BID_OBJECT_TEMPLATE,
  IPAP_SETID_ASK_OBJECT_TEMPLATE,
  IPAP_OPTNS_ASK_OBJECT_TEMPLATE,
  IPAP_SETID_ALLOC_OBJECT_TEMPLATE,
  IPAP_OPTNS_ALLOC_OBJECT_TEMPLATE ) = (0,1,2,3,4,5,6,7)

( KNOWN,
  UNKNOWN
  ) = (0,1)

(
IPAP_INVALID,
IPAP_AUCTION,
IPAP_BID,
IPAP_ASK,
IPAP_ALLOCATION,
IPAP_MAX_OBJECT_TYPE
) = (-1, 0, 1, 2, 3, 4)

class IpapTemplate:

    def __init__(self):
        self.obj = lib.ipap_template_new()

    def set_id(self, id : int):
        return lib.ipap_template_set_id(self.obj,c_uint16(id))

    def set_max_fields(self, max_fields : int):
        lib.ipap_template_set_maxfields(self.obj,c_int(max_fields))

    def set_type(self, type: int):
        lib.ipap_template_set_type(self.obj, c_int(type))

    def _get_template_type_mandatory_field_size(self, temp_type : int) -> int:
        return lib.ipap_template_get_template_type_mandatory_field_size(self.obj, c_int(temp_type))

    def get_template_type_mandatory_field(self, temp_type : int) -> list:
        size = self._get_template_type_mandatory_field_size(temp_type)
        list_return = []

        for i in range(0,size):
            obj = lib.ipap_template_get_template_type_mandatory_field(self.obj, c_int(temp_type), c_int(i))

            if obj: # not null
                field_key = IpapFieldKey(obj)
                list_return.append(field_key)
            else:
                raise ValueError('Field key not found')
        return list_return

    def set_id(self, id : int):
        lib.ipap_template_set_id(self.obj, c_uint16(id))

    def set_max_fields(self, max_fields : int):
        lib.ipap_template_set_maxfields(self.obj, max_fields)

    def set_type(self, type :int):
        lib.ipap_template_set_type(self.obj, c_int(type))

    def add_field(self,field_size : int, encodeNetwork : int, field : IpapField):
        lib.ipap_template_add_field(self.obj, c_uint16(field_size), c_uint8(KNOWN), c_int(encodeNetwork), field.obj)

    def _get_object_template_types_size(self, object_type : int):
        lib.ipap_template_get_object_template_types_size(self.obj, c_uint8(object_type))

    def get_object_template_types(self, object_type : int):
        size = self._get_object_template_types_size(object_type)
        list_return = []

        for i in range(0,size):
            templ_type = lib.ipap_template_get_object_template_types_at_pos(self.obj, c_int(object_type), c_int(i))

            if templ_type == IPAP_INVALID:
                raise ValueError('template Type reququested but not found')
            else:
                list_return.append(templ_type)

        return list_return
