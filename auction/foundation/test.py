import unittest
from foundation.field_def_manager import FieldDefManager
from foundation.field_def_manager import DataType
from foundation.ipap_message_parser import IpapMessageParser
from foundation.auction_parser import AuctionXmlFileParser
from foundation.bidding_object_file_parser import BiddingObjectXmlFileParser
from foundation.module_loader import ModuleLoader
from foundation.database_manager import DataBaseManager
from foundation.config import Config
from foundation.field_value import FieldValue
from foundation.specific_field_value import SpecificFieldValue
from foundation.id_source import IdSource

from python_wrapper.ipap_template import ObjectType
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_message import IpapMessage
from python_wrapper.ipap_data_record import IpapDataRecord
from python_wrapper.ipap_value_field import IpapValueField
from python_wrapper.ipap_template_container import IpapTemplateContainerSingleton

import aiounittest


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
        field_found = self.def_file_manager.get_field_by_code(0, 31)
        self.assertEqual(field_found['name'], "AlgorithmName")

        # Field not found
        with self.assertRaises(ValueError):
            field_not_found = self.def_file_manager.get_field_by_code(0, 310)

        # Field not found
        with self.assertRaises(ValueError):
            field_not_found = self.def_file_manager.get_field_by_code(100, 31)

    def test_get_field_value(self):
        field_value = self.def_file_manager.get_field_value('IpAddr', 'srcip')
        self.assertEqual(field_value, '190.0.0.1')

        # Field Value not found
        with self.assertRaises(ValueError):
            field_value = self.def_file_manager.get_field_value('Type', 'srcip0')

        # Field Value not found
        with self.assertRaises(ValueError):
            field_value = self.def_file_manager.get_field_value('Type2', 'srcip')


class FieldValueTest(unittest.TestCase):

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
        set_name, auction_name = self.ipap_message_parser.parse_name(auction_id)
        self.assertEqual(set_name, "1")
        self.assertEqual(auction_name, "5")

        auction_id = "sees.asdasd"
        set_name, auction_name = self.ipap_message_parser.parse_name(auction_id)
        self.assertEqual(set_name, "sees")
        self.assertEqual(auction_name, "asdasd")

        auction_id = ""
        with self.assertRaises(ValueError):
            set_name, auction_name = self.ipap_message_parser.parse_name(auction_id)

    def test_parse_object_type(self):
        stype = "auction"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_AUCTION, ret)

        stype = "bid"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_BID, ret)

        stype = "ask"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ASK, ret)

        stype = "allocation"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ALLOCATION, ret)

        stype = "0"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_AUCTION, ret)

        stype = "1"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_BID, ret)

        stype = "2"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ASK, ret)

        stype = "3"
        ret = self.ipap_message_parser.parse_object_type(stype)
        self.assertEqual(ObjectType.IPAP_ALLOCATION, ret)

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

    def test_read_template(self):
        ipap_message = IpapMessage(1, 1, False)
        template_id = ipap_message.new_data_template(10, TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        ipap_message.add_field(template_id, 0, 30)

        ipap_data_record = IpapDataRecord(templ_id=template_id)
        ipap_field_value1 = IpapValueField()
        value = 12231213
        ipap_field_value1.set_value_uint64(value)

        # Replace the value
        ipap_data_record.insert_field(0, 30, ipap_field_value1)
        ipap_message.include_data(template_id, ipap_data_record)

        template = self.ipap_message_parser.read_template(ipap_message, TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        self.assertEqual(template.get_type(), TemplateType.IPAP_SETID_AUCTION_TEMPLATE)

        with self.assertRaises(ValueError):
            template = self.ipap_message_parser.read_template(ipap_message, TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE)

    def test_read_data_records(self):
        ipap_message = IpapMessage(1, 1, False)
        template_id = ipap_message.new_data_template(10, TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        ipap_message.add_field(template_id, 0, 30)

        ipap_data_record = IpapDataRecord(templ_id=template_id)
        ipap_field_value1 = IpapValueField()
        value = 12231213
        ipap_field_value1.set_value_uint64(value)

        # Replace the value
        ipap_data_record.insert_field(0, 30, ipap_field_value1)
        ipap_message.include_data(template_id, ipap_data_record)

        lst = self.ipap_message_parser.read_data_records(ipap_message, template_id)
        self.assertEqual(len(lst), 1)

        lst = self.ipap_message_parser.read_data_records(ipap_message, 100)
        self.assertEqual(len(lst), 0)

    def test_get_domain(self):
        domain = self.ipap_message_parser.get_domain()
        self.assertEqual(domain, 10)


class AuctionXmlFileParserTest(unittest.TestCase):

    def setUp(self):
        self.auction_xml_file_parser = AuctionXmlFileParser(10)

    def test_parse(self):
        lst_auctions = self.auction_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions1.xml")

        self.assertEqual(len(lst_auctions), 1)
        auction = lst_auctions[0]

        # verifies the interval
        time_between = auction.interval.stop - auction.interval.start
        self.assertEqual(auction.interval.duration, 100000)
        self.assertEqual(auction.interval.interval, 10)

        self.template_container = IpapTemplateContainerSingleton()
        exists = self.template_container.exists_template(
            auction.bidding_object_templates[ObjectType.IPAP_BID][TemplateType.IPAP_OPTNS_BID_OBJECT_TEMPLATE])
        self.assertEqual(exists, True)

        templ_bid_data = auction.bidding_object_templates[ObjectType.IPAP_BID][
            TemplateType.IPAP_SETID_BID_OBJECT_TEMPLATE]
        ipap_template = self.template_container.get_template(templ_bid_data)

        found = False
        field_list = ipap_template.get_fields()
        for field in field_list:
            if field.get_field_name().decode('ascii') == "auctionUnitValue":
                found = True

        self.assertEqual(found, True)
        self.assertEqual(auction.resource_key, "1.router1")
        self.assertEqual(auction.get_key(), "1.10")
        self.assertEqual(len(auction.misc_dict), 2)

        # Verifies the action that was created.
        self.assertEqual(auction.action.name, "libbas")
        self.assertEqual(auction.action.default_action, True)
        self.assertEqual(len(auction.action.config_dict), 0)

    def test_parse_maby_auctions(self):
        lst_auctions = self.auction_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions4.xml")

        self.assertEqual(len(lst_auctions), 3)


class BiddingObjectXmlFileParserTest(unittest.TestCase):

    def setUp(self):
        self.bidding_xml_file_parser = BiddingObjectXmlFileParser(10)

    def test_parse(self):
        lst_bids = self.bidding_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_bids1.xml")

        self.assertEqual(len(lst_bids), 1)
        bidding_object = lst_bids[0]

        self.assertEqual(bidding_object.get_parent_key(), "1.1")
        self.assertEqual(bidding_object.get_key(), "bid1")
        self.assertEqual(len(bidding_object.elements), 2)
        self.assertEqual(len(bidding_object.options), 2)

        # Verifies the first element
        element = bidding_object.elements['element1']
        self.assertEqual(element['quantity'].value, "1")

        # Verifies the first option
        option = bidding_object.options['option1']
        self.assertEqual(option['biddingduration'].value, "600")

    def test_parse_many_auctions(self):
        lst_bids = self.bidding_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_bids2.xml")

        self.assertEqual(len(lst_bids), 2)


class BiddingObjectTest(aiounittest.AsyncTestCase):

    async def test_parse(self):
        self.bidding_xml_file_parser = BiddingObjectXmlFileParser(10)
        self.config = Config('auction_agent.yaml')
        self.data_base = DataBaseManager(self.config.get_config_param('DataBase', 'Type'),
                                         self.config.get_config_param('DataBase', 'Host'),
                                         self.config.get_config_param('DataBase', 'User'),
                                         self.config.get_config_param('DataBase', 'Password'),
                                         self.config.get_config_param('DataBase', 'Port'),
                                         self.config.get_config_param('DataBase', 'DbName'),
                                         self.config.get_config_param('DataBase', 'Minsize'),
                                         self.config.get_config_param('DataBase', 'Maxsize'))

        lst_bids = self.bidding_xml_file_parser.parse(
            "/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_bids1.xml")

        self.assertEqual(len(lst_bids), 1)
        bidding_object = lst_bids[0]
        bidding_object.set_session("session_1")
        self.assertEqual(bidding_object.get_parent_key(), "1.1")
        self.assertEqual(bidding_object.get_key(), "1.bid1")
        self.assertEqual(len(bidding_object.elements), 2)
        self.assertEqual(len(bidding_object.options), 2)

        # Verifies the first element
        element = bidding_object.elements['element1']
        self.assertEqual(element['quantity'].value, "1")

        # Verifies the first option
        option = bidding_object.options['option1']
        self.assertEqual(option['biddingduration'].value, "600")

        connect = await self.data_base.acquire()

        await bidding_object.store(connect)



class ModuleLoaderTest(unittest.TestCase):

    def setUp(self):
        module_directory = '/home/ns3/py_charm_workspace/paper_subastas/auction/proc_modules'
        self.module_loader = ModuleLoader(module_directory, "AUMProcessor", None)

    def test_load_module(self):
        module_name = 'basic_server_module'
        module = self.module_loader.load_module(module_name, False)
        self.assertEqual(module is not None, True)

        with self.assertRaises(ModuleNotFoundError):
            module_name = 'basic_asda_module'
            module2 = self.module_loader.load_module(module_name, False)

        with self.assertRaises(ValueError):
            module_name = ''
            module2 = self.module_loader.load_module(module_name, False)

    def test_get_module(self):
        module_name = 'basic_server_module'
        self.module_loader.load_module(module_name, False)
        module = self.module_loader.get_module(module_name)
        self.assertEqual(module is not None, True)

        module_name = 'basic_test'
        with self.assertRaises(ModuleNotFoundError):
            module2 = self.module_loader.get_module(module_name)

    def test_release_module(self):
        module_name = 'basic_server_module'
        self.module_loader.load_module(module_name, False)
        self.module_loader.release_module(module_name)
        self.assertEqual(len(self.module_loader.modules), 0)


class SourceIdTest(unittest.TestCase):

    def test_get_ids(self):
        self.id_source = IdSource()
        id1 = self.id_source.new_id()
        id2 = self.id_source.new_id()
        id3 = self.id_source.new_id()
        self.id_source.free_id(id1)
        self.id_source.free_id(id2)
        id4 = self.id_source.new_id()
        self.id_source.free_id(id3)
        print(self.id_source.num)
        self.id_source.free_id(id4)

        self.assertEqual(id4, 1)
        print(self.id_source.num)


class SourceIdUniqueTest(unittest.TestCase):

    def test_get_id_unique(self):
        self.id_source = IdSource(True)
        id1 = self.id_source.new_id()
        id2 = self.id_source.new_id()
        id3 = self.id_source.new_id()
        self.id_source.free_id(id1)
        self.id_source.free_id(id2)
        id4 = self.id_source.new_id()
        self.id_source.free_id(id3)
        print(self.id_source.num)
        self.id_source.free_id(id4)

        self.assertEqual(id4, 4)
        print(self.id_source.num)
