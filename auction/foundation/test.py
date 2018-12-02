import unittest
from foundation.field_def_manager import FieldDefManager
from foundation.field_def_manager import DataType
from foundation.ipap_message_parser import IpapMessageParser
from foundation.field_value import FieldValue
from foundation.specific_field_value import SpecificFieldValue
from python_wrapper.ipap_template import ObjectType
from python_wrapper.ipap_template import TemplateType


class DefFileManagerTest(unittest.TestCase):

    def setUp(self):
        self.def_file_manager = FieldDefManager()

    def test_get_field_defs(self):
        field_defs = self.def_file_manager.get_field_defs()
        self.assertEqual(len(field_defs), 51)

    def test_get_field_vals(self):
        field_vals = self.def_file_manager.get_field_vals()
        self.assertEqual(len(field_vals), 1)

    def test_get_field(self):
        # Field found
        field_found = self.def_file_manager.get_field("templatelist")
        self.assertEqual(field_found['type'], DataType.STRING)

        # Field not found
        with self.assertRaises(ValueError):
            field_not_found = self.def_file_manager.get_field("templatelist0")

    def test_get_field_by_code(self):
        field_found = self.def_file_manager.get_field_by_code(0,31)
        self.assertEqual(field_found['name'], "AlgorithmName")

        # Field not found
        with self.assertRaises(ValueError):
            field_not_found = self.def_file_manager.get_field_by_code(0,310)

        # Field not found
        with self.assertRaises(ValueError):
            field_not_found = self.def_file_manager.get_field_by_code(100,31)

    def test_get_field_value(self):
        field_value = self.def_file_manager.get_field_value('IpAddr', 'srcip')
        self.assertEqual(field_value, '190.0.0.1')

        # Field Value not found
        with self.assertRaises(ValueError):
            field_value = self.def_file_manager.get_field_value('Type', 'srcip0')

        # Field Value not found
        with self.assertRaises(ValueError):
            field_value = self.def_file_manager.get_field_value('Type2', 'srcip')


class FieldTest(unittest.TestCase):

    def test_parse_field_value(self):

        field_value = FieldValue()

        value = "*"
        field_value.parse_field_value(value)
        self.assertEqual(field_value.cnt_values, 0)

        value = "10-50"
        field_value.parse_field_value(value)
        self.assertEqual(field_value.cnt_values, 2)

        value = "1,2,3,4,5,67"
        field_value.parse_field_value(value)
        self.assertEqual(field_value.cnt_values, 6)

        value = "Invalid"
        field_value.parse_field_value(value)
        self.assertEqual(field_value.cnt_values, 1)


class SpecificFieldValueTest(unittest.TestCase):

    def test_set_field_type(self):
        field_value = SpecificFieldValue()
        field_value.set_field_type("string")
        self.assertEqual(field_value.field_type, "string")

        field_value.set_field_type(5)

    def test_set_value(self):
        field_value = SpecificFieldValue()
        field_value.set_value("asdasd")
        self.assertEqual(field_value.value, "asdasd")


class IpapMessageParserTest(unittest.TestCase):

    def setUp(self):
        self.ipap_message_parser = IpapMessageParser(10)

    def test_parse_name(self):
        auction_id = "1"
        set_name, auction_name = self.ipap_message_parser.parse_name(auction_id)
        self.assertEqual(set_name, "")
        self.assertEqual(auction_name, "1")

        auction_id = "1.5"
        set_name, auction_name =  self.ipap_message_parser.parse_name(auction_id)
        self.assertEqual(set_name, "1")
        self.assertEqual(auction_name, "5")

        auction_id = "sees.asdasd"
        set_name, auction_name =  self.ipap_message_parser.parse_name(auction_id)
        self.assertEqual(set_name, "sees")
        self.assertEqual(auction_name, "asdasd")

        auction_id = ""
        with self.assertRaises(ValueError):
            set_name, auction_name = self.ipap_message_parser.parse_name(auction_id)

    def test_parse_object_type(self):
        stype = "auction"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_AUCTION,ret)

        stype = "bid"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_BID,ret)

        stype = "ask"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ASK,ret)

        stype = "allocation"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ALLOCATION,ret)

        stype = "0"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_AUCTION,ret)

        stype = "1"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_BID,ret)

        stype = "2"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ASK,ret)

        stype = "3"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ALLOCATION,ret)

        stype = "4"
        with self.assertRaises(ValueError):
            ret = self.ipap_message_parser.parse_object_type(stype)

        stype = "skadjkdk"
        with self.assertRaises(ValueError):
            ret = self.ipap_message_parser.parse_object_type(stype)

    def test_parse_template_type(self):

        templ_type = "data"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_AUCTION, templ_type)
        self.assertEqual(TemplateType.IPAP_SETID_AUCTION_TEMPLATE, ret)

        templ_type = "option"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_AUCTION, templ_type)
        self.assertEqual(TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE, ret)

        templ_type = "data"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_BID, templ_type)
        self.assertEqual(TemplateType.IPAP_SETID_BID_OBJECT_TEMPLATE, ret)

        templ_type = "option"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_BID, templ_type)
        self.assertEqual(TemplateType.IPAP_OPTNS_BID_OBJECT_TEMPLATE, ret)

        templ_type = "data"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_ASK, templ_type)
        self.assertEqual(TemplateType.IPAP_SETID_ASK_OBJECT_TEMPLATE, ret)

        templ_type = "option"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_ASK, templ_type)
        self.assertEqual(TemplateType.IPAP_OPTNS_ASK_OBJECT_TEMPLATE, ret)

        templ_type = "data"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_ALLOCATION, templ_type)
        self.assertEqual(TemplateType.IPAP_SETID_ALLOC_OBJECT_TEMPLATE, ret)

        templ_type = "option"
        ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_ALLOCATION, templ_type)
        self.assertEqual(TemplateType.IPAP_OPTNS_ALLOC_OBJECT_TEMPLATE, ret)

        templ_type = "optasda"
        with self.assertRaises(ValueError):
            ret = self.ipap_message_parser.parse_template_type(ObjectType.IPAP_ALLOCATION, templ_type)

    def test_get_domain(self):
        domain = self.ipap_message_parser.get_domain()
        self.assertEqual(domain, 10)