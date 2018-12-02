from python_wrapper.ipap_field_type import IpapFieldType
from python_wrapper.ipap_field import IpapField
from python_wrapper.ipap_value_field import IpapValueField
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_template import UnknownField
from python_wrapper.ipap_template import ObjectType
from python_wrapper.ipap_template_container import IpapTemplateContainer

from ctypes import pointer
import unittest


class IpapFieldTypeTest(unittest.TestCase):
    """
    IpapFieldTypeTest
    """
    def setUp(self):
        self.ftype = IpapFieldType()

    def test_setters(self):
        self.eno = 10
        self.ftype = 10
        self.length = 10
        self.name = b"casa"
        self.xmlname = b"casa"
        self.documentation = b"casa"

class IpapFieldTest(unittest.TestCase):
    """

    """
    def setUp(self):
        self.ipap_field = IpapField()
        self.ipap_field.set_field_type(0, 30, 8,  3, b"campo_1", b"campo_2", b"campo_3")

    def test_get_eno(self):
        self.assertEqual(self.ipap_field.get_eno(), 0)

    def test_get_type(self):
        self.assertEqual(self.ipap_field.get_type(), 30)

    def test_get_length(self):
        self.assertEqual(self.ipap_field.get_length(), 8)

    def test_get_field_name(self):
        self.assertEqual(self.ipap_field.get_field_name(), b"campo_1")

    def test_get_xml_name(self):
        self.assertEqual(self.ipap_field.get_xml_name(), b"campo_2")

    def test_get_documentation(self):
        self.assertEqual(self.ipap_field.get_documentation(), b"campo_3")


class IpapValueFieldTest(unittest.TestCase):
    """

    """
    def setUp(self):
        self.ipap_field_value = IpapValueField()

    def test_set_value_uint8(self):
        value = 12
        self.ipap_field_value.set_value_uint8(value)
        val = self.ipap_field_value.get_value_uint8()
        self.assertEqual(value, val)

    def test_set_value_uint16(self):
        value = 123
        self.ipap_field_value.set_value_uint16(value)
        val = self.ipap_field_value.get_value_uint16()
        self.assertEqual(value, val)

    def test_set_value_uint32(self):
        value = 213233
        self.ipap_field_value.set_value_uint32(value)
        val = self.ipap_field_value.get_value_uint32()
        self.assertEqual(value, val)

    def test_set_value_uint64(self):
        value = 123187623
        self.ipap_field_value.set_value_uint64(value)
        val = self.ipap_field_value.get_value_uint64()
        self.assertEqual(value, val)

    def test_set_value_float32(self):
        value = 12.46
        self.ipap_field_value.set_value_float32(value)
        val = self.ipap_field_value.get_value_float()
        val = round(val,2)
        self.assertEqual(value, val)

    def test_set_value_double(self):
        value = 12121.45
        self.ipap_field_value.set_value_double(value)
        val = self.ipap_field_value.get_value_double()
        self.assertEqual(value, val)

    def test_set_value_vchar(self):
        value = b"assd"
        self.ipap_field_value.set_value_vchar(value, len(value))
        val = self.ipap_field_value.get_value_vchar()
        self.assertEqual(value, val)


class IpapFieldKeyTest(unittest.TestCase):
    """
    IpapFieldKeyTest
    """
    def setUp(self):
        self.ipap_field_key1 = IpapFieldKey(1, 30)

    def test_get_eno(self):
        val = self.ipap_field_key1.get_eno()
        self.assertEqual(val, 1)

    def test_get_ftype(self):
        val = self.ipap_field_key1.get_ftype()
        self.assertEqual(val, 30)

    def test_get_key(self):
        val = self.ipap_field_key1.get_key()
        self.assertEqual(val, "1-30")


class TemplateTest(unittest.TestCase):

    def setUp(self):
        self.template = IpapTemplate()
        _id = 12
        self.template.set_id(_id)

    def test_set_max_fields(self):
        num_fields = 10
        self.template.set_max_fields(num_fields)

    def test_set_type(self):
        self.template.set_type(TemplateType.IPAP_SETID_AUCTION_TEMPLATE)

    def test_get_template_type_mandatory_field(self):
        mandatory_fields = self.template.get_template_type_mandatory_field(
                                    TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        self.assertEqual(len(mandatory_fields), 12)

    def test_add_field(self):
        ipap_field = IpapField()
        ipap_field.set_field_type(0, 30, 8,  3, b"campo_1", b"campo_2", b"campo_3")
        self.template.add_field(8, UnknownField.KNOWN,ipap_field)

    def test_get_type(self):
        self.template.set_type(TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        template_type = self.template.get_type()
        self.assertEqual(template_type, TemplateType.IPAP_SETID_AUCTION_TEMPLATE)

    def test_get_object_template_types(self):
        with self.assertRaises(ValueError):
            lst = self.template.get_object_template_types(ObjectType.IPAP_INVALID)

        lst = self.template.get_object_template_types(ObjectType.IPAP_AUCTION)
        self.assertEqual(len(lst), 2)


class TemplateContainerTest(unittest.TestCase):

    def setUp(self):
        print('in setUp')
        self.template_container = IpapTemplateContainer()

    def test_add_template(self):
        print('in test_add_template')
        ipap_field = IpapField()
        ipap_field.set_field_type(0, 30, 8,  3, b"campo_1", b"campo_2", b"campo_3")

        _id = 12
        template = IpapTemplate()
        template.set_id(_id)
        template.set_type(TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        template.add_field(8, UnknownField.KNOWN, ipap_field)

        self.template_container.add_template(template)

    def test_delete_all_templates(self):
        print('in test_delete_all_templates')
        ipap_field = IpapField()
        ipap_field.set_field_type(0, 30, 8,  3, b"campo_1", b"campo_2", b"campo_3")

        _id = 12
        template = IpapTemplate()
        template.set_id(_id)
        template.set_type(TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        template.add_field(8, UnknownField.KNOWN, ipap_field)

        self.template_container.add_template(template)
        self.template_container.delete_all_templates()
        val = self.template_container.get_num_templates()
        self.assertEqual(val, 0)

    def test_delete_template(self):
        ipap_field = IpapField()
        ipap_field.set_field_type(0, 30, 8,  3, b"campo_1", b"campo_2", b"campo_3")

        _id = 12
        template = IpapTemplate()
        template.set_id(_id)
        template.set_type(TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        template.add_field(8, UnknownField.KNOWN, ipap_field)

        self.template_container.add_template(template)
        self.template_container.delete_template(_id)
        val = self.template_container.get_num_templates()
        self.assertEqual(val, 0)

    def test_exists_template(self):
        ipap_field = IpapField()
        ipap_field.set_field_type(0, 30, 8,  3, b"campo_1", b"campo_2", b"campo_3")

        _id = 12
        template = IpapTemplate()
        template.set_id(_id)
        template.set_type(TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        template.add_field(8, UnknownField.KNOWN, ipap_field)
        self.template_container.add_template(template)

        val = self.template_container.exists_template(_id)
        self.assertEqual(val, True)

        _id = 13
        val = self.template_container.exists_template(_id)
        self.assertEqual(val, False)


class FieldContainerTest(unittest.TestCase):
    """
    FieldContainerTest
    """
    def setUp(self):
        self.field_container = IpapFieldContainer()

    def test_get_field(self):
        self.field_container.initialize_forward()
        field = self.field_container.get_field(0,30)
        self.assertEqual(field.get_field_name(), b"endMilliSeconds")

        with self.assertRaises(ValueError):
            field2 = self.field_container.get_field(0,3000)

    def test_not_initialized(self):
        with self.assertRaises(ValueError):
            field = self.field_container.get_field(0, 30)


class IpapDataRecordTest(unittest.TestCase):
    """
    IpapDataRecordTest
    """
    def setUp(self):
        self.ipap_data_record = IpapDataRecord(templ_id=2)

    def test_get_template_id(self):
        value = self.ipap_data_record.get_template_id()
        self.assertEqual(value,2)

    def test_insert_field(self):

        ipap_field_value1 = IpapValueField()
        value = 12
        ipap_field_value1.set_value_uint8(value)

        ipap_field_value2 = IpapValueField()
        value = 13
        ipap_field_value2.set_value_uint8(value)

        # Replace the value
        self.ipap_data_record.insert_field(0, 30, ipap_field_value1)
        self.ipap_data_record.insert_field(0, 30, ipap_field_value2)
        num_fields = self.ipap_data_record.get_num_fields()
        self.assertEqual(num_fields,1)

        self.ipap_data_record.insert_field(0, 31, ipap_field_value2)
        num_fields = self.ipap_data_record.get_num_fields()
        self.assertEqual(num_fields,2)

