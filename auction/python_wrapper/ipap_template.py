from ctypes import cdll
from ctypes import c_int
from ctypes import c_uint16
from ctypes import c_uint8
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_field import IpapField
from enum import Enum

lib = cdll.LoadLibrary('libipap.so')


class TemplateType(Enum):
    IPAP_INVALID_TEMPLATE = -1
    IPAP_SETID_AUCTION_TEMPLATE = 0
    IPAP_OPTNS_AUCTION_TEMPLATE = 1
    IPAP_SETID_BID_OBJECT_TEMPLATE = 2
    IPAP_OPTNS_BID_OBJECT_TEMPLATE = 3
    IPAP_SETID_ASK_OBJECT_TEMPLATE = 4
    IPAP_OPTNS_ASK_OBJECT_TEMPLATE = 5
    IPAP_SETID_ALLOC_OBJECT_TEMPLATE = 6
    IPAP_OPTNS_ALLOC_OBJECT_TEMPLATE = 7


class UnknownField(Enum):
    KNOWN = 0
    UNKNOWN = 1


class ObjectType(Enum):
    IPAP_INVALID = -1
    IPAP_AUCTION = 0
    IPAP_BID = 1
    IPAP_ASK = 2
    IPAP_ALLOCATION = 3
    IPAP_MAX_OBJECT_TYPE = 4


class IpapTemplate:

    def __init__(self, obj=None):
        if obj:
            self.obj = obj
        else:
            self.obj = lib.ipap_template_new()

    def set_id(self, id_template: int):
        return lib.ipap_template_set_id(self.obj, c_uint16(id_template))

    def get_template_id(self) -> int:
        return lib.ipap_template_get_template_id(self.obj)

    def set_max_fields(self, max_fields: int):
        lib.ipap_template_set_maxfields(self.obj, c_int(max_fields))

    def set_type(self, templ_type: TemplateType):
        lib.ipap_template_set_type(self.obj, c_int(templ_type.value))

    def _get_template_type_mandatory_field_size(self, temp_type: TemplateType) -> int:
        return lib.ipap_template_get_template_type_mandatory_field_size(self.obj, c_int(temp_type.value))

    def get_template_type_mandatory_field(self, temp_type: TemplateType) -> list:
        size = self._get_template_type_mandatory_field_size(temp_type)
        if size < 0:
            raise ValueError('The template type given is not valid')

        list_return = []

        for i in range(0, size):
            obj = lib.ipap_template_get_template_type_mandatory_field(self.obj, c_int(temp_type.value), c_int(i))
            if obj:  # not null
                field_key = IpapFieldKey(obj=obj)
                list_return.append(field_key)
            else:
                raise ValueError('Field key not found')
        return list_return

    def _get_template_type_key_size(self, temp_type: TemplateType) -> int:
        return lib.ipap_template_get_template_type_keys_size(self.obj, c_int(temp_type.value))

    def get_template_type_key_field(self, temp_type: TemplateType) -> list:
        size = self._get_template_type_key_size(temp_type)
        if size < 0:
            raise ValueError('The template type given is not valid')

        list_return = []

        for i in range(0, size):
            obj = lib.ipap_template_get_template_type_key(self.obj, c_int(temp_type.value), c_int(i))
            if obj:  # not null
                field_key = IpapFieldKey(obj=obj)
                list_return.append(field_key)
            else:
                raise ValueError('Field key not found')
        return list_return

    def add_field(self, field_size: int, unknow_field: UnknownField, encode_network: bool, field: IpapField):
        if encode_network:
            i_encode_network = 1
        else:
            i_encode_network = 0

        lib.ipap_template_add_field(self.obj, c_uint16(field_size),
                                    c_uint8(unknow_field.value), c_int(i_encode_network), field.obj)

    def get_type(self) -> TemplateType:
        return TemplateType(lib.ipap_template_get_type(self.obj))

    def get_object_type(self, template_type: TemplateType) -> ObjectType:
        object_type = lib.ipap_template_get_object_type(self.obj,c_uint8(template_type.value))
        return ObjectType(object_type)

    def _get_object_template_types_size(self, object_type: ObjectType) -> int:
        if object_type == ObjectType.IPAP_INVALID:
            return -1
        else:
            return lib.ipap_template_get_object_template_types_size(self.obj, c_uint8(object_type.value))

    def get_object_template_types(self, object_type: ObjectType):
        if object_type == ObjectType.IPAP_INVALID:
            raise ValueError("Invalid object type")

        size = self._get_object_template_types_size(object_type)
        list_return = []

        for i in range(0, size):
            templ_type = TemplateType(lib.ipap_template_get_object_template_types_at_pos(
                self.obj, c_int(object_type.value), c_int(i)))

            if templ_type == object_type.IPAP_INVALID:
                raise ValueError('Object type requested but not found')
            else:
                list_return.append(templ_type)

        return list_return

    def get_fields(self) -> list:
        size = lib.ipap_template_get_numfields(self.obj)
        list_return = []

        for i in range(0, size):
            obj = lib.ipap_template_get_field_by_pos(self.obj, c_int(i))
            if obj:  # not null
                field = IpapField(obj=obj)
                list_return.append(field)
            else:
                raise ValueError('Field key not found')
        return list_return

    def get_field(self, eno: int, ftype: int) -> IpapField:
        obj = lib.ipap_template_get_field(self.obj, c_int(eno), c_int(ftype))
        if obj:  # not null
            field = IpapField(obj=obj)
            return field
        else:
            raise ValueError('Field with eno {0} and ftype {1} was not found'.format(str(eno), str(ftype)))

    def __eq__(self, other):
        return lib.ipap_template_is_equal(self.obj, other.obj)

    def get_num_fields(self) -> int:
        return lib.ipap_template_get_numfields(self.obj)

    @staticmethod
    def get_data_template(object_type: ObjectType) -> TemplateType:

        if object_type == ObjectType.IPAP_AUCTION:
            return TemplateType.IPAP_SETID_AUCTION_TEMPLATE

        elif object_type == ObjectType.IPAP_BID:
            return TemplateType.IPAP_SETID_BID_OBJECT_TEMPLATE

        elif object_type == ObjectType.IPAP_ALLOCATION:
            return TemplateType.IPAP_SETID_ALLOC_OBJECT_TEMPLATE

        elif object_type == ObjectType.IPAP_ASK:
            return TemplateType.IPAP_SETID_ASK_OBJECT_TEMPLATE

        else:
            return TemplateType.IPAP_INVALID_TEMPLATE

    @staticmethod
    def get_opts_template(object_type: ObjectType) -> TemplateType:

        if object_type == ObjectType.IPAP_AUCTION:
            return TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE

        elif object_type == ObjectType.IPAP_BID:
            return TemplateType.IPAP_OPTNS_BID_OBJECT_TEMPLATE

        elif object_type == ObjectType.IPAP_ALLOCATION:
            return TemplateType.IPAP_OPTNS_ALLOC_OBJECT_TEMPLATE

        elif object_type == ObjectType.IPAP_ASK:
            return TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE

        else:
            return TemplateType.IPAP_INVALID_TEMPLATE

    def __del__(self):
        if self.obj:  # not null
            lib.ipap_template_destroy(self.obj)

