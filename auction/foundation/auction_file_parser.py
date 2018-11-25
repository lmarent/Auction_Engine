from lxml import etree
from foundation.auction import AuctionTemplateField
from foundation.parse_format import ParseFormats
from foundation.field_def_manager import FieldDefManager
from foundation.ipap_message_parser import
from python_wrapper.ipap_field_container import IpApFieldContainer

class AuctionXmlFileParser(IpapMessageParser):
    """
    This class parses file and ipap messages containing auction definitions.


    A configuration item is a tuple of three values:
        name : name of the configuration item
        type : type of the configuration item
        value: value in string.

    """

    def __init__(self, config):
        self.config = config

    @staticmethod
    def _parse_config_item(self, item):
        """
        Parse a configuration item.

        :param item: item to be parsed.
        :return:
        """
        name = item.get("NAME").lower()
        type = item.get("TYPE").lower()
        value = item.text
        if not name:
            raise ValueError("The xml has a preference with no name")

        if not type:
            raise ValueError("The xml has a preference with no type")

            ParseFormats.parse_item(type, value)
        return (name, type, value)

    def _parse_global_options(self, item):
        """
        Parse global options within the xml
        :param item: Global Tag
        :return: list fo configuraion items.
        """
        prefs = []
        for subitem in item.iterchildren():
            if subitem.tag.lower() == "pref":
                pref = self._parse_pref(subitem)
                prefs.append(pref)
        return prefs

    def parse_object_type(self, object_type_str : str):

    def parse_template_type(self, object_type, template_type_str : str):



    def _parse_field(self, node, field_container : IpApFieldContainer):
        """
        Parse a field from the auction xml

        :param node: node that represents the field in the xml
        :return
        """
        field_name = node.get("NAME")
        field_def_manager = FieldDefManager()
        field_def  = field_def_manager.get_field(field_name)
        auction_template_field = AuctionTemplateField(field_def, field_def.Length)
        belogs_to = []
        for item in node.iterchildren():
            if item.tag == "TEMPLATE_FIELD":
                object_type = parse_object_type(item.get("OBJECT_TYPE"))
                template_type = parse_template_type(object_type, item.get("TEMPLATE_TYPE"))
                belogs_to.append((object_type, template_type))

        auction_template_field.field_belong_to = belogs_to
        return auction_template_field


    def _parse_auctions(self, item)


    def parse(self, field_definitions : dict, file_name : str ) -> list:
        """
        parse the auction with the file given as parameter
        :param file_name file name including the absolute path of te file to parse.

        :return: list of auctions in the file
        """
        the_dtd = self.config.AUCTIONFILE_DTD
        root_node = self.config.DTD_ROOT_NODE

        parser = etree.XMLParser(dtd_validation=True)
        dtd = etree.DTD(open(the_dtd))
        tree = etree.parse(file_name)
        valid = dtd.validate(tree)

        if (valid):
            raise ValueError("XML given is valid!")

        root = tree.getroot()
        id = root.ID.lower()

        global_element = root.Element("GLOBAL")
        for item in root.iterchildren():
            if item.tag.lower() == "global":
                self._parse_global_options(item)
            elif item.tag.lower() == "auction":
                self._parse_auctions(item)


