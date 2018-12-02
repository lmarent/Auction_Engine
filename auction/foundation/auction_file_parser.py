from lxml import etree
from lxml.etree import Element
from foundation.auction import AuctionTemplateField
from foundation.auction import Action
from foundation.auction import Auction
from foundation.parse_format import ParseFormats
from foundation.field_def_manager import FieldDefManager
from foundation.ipap_message_parser import IpapMessageParser
from foundation.config import Config
from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_template_container import IpapTemplateContainer

import pathlib
import os
from copy import deepcopy


class AuctionXmlFileParser(IpapMessageParser):
    """
    This class parses file and ipap messages containing auction definitions.


    A configuration item is a tuple of three values:
        name : name of the configuration item
        type : type of the configuration item
        value: value in string.

    """

    def __init__(self, domain: int):
        super(AuctionXmlFileParser, self).__init__(domain=domain)

    @staticmethod
    def _parse_action(node: Element):

        action_name = node.get("NAME").lower()

        # Verifies that a name was given to the action.
        if not action_name:
            raise ValueError("Auction Parser Error: missing name at line {0}".format(str(node.sourceline)))

        action = Action(action_name, False, dict())

        for item in node.iterchildren():
            if isinstance(item.tag, str):
                if item.tag.lower() == "pref":
                    (name, type, value) = _parse_config_item(item)
                    action.add_config_item(name, type, value)

        return action

    def _parse_global_options(self, item: Element) -> (dict, dict):
        """
        Parse global options within the xml
        :param item: Global Tag
        :return: dictionary of configuration items.
                list of actions.
        """
        global_misc = {}
        global_actions = {}

        for sub_item in item.iterchildren():
            if isinstance(sub_item.tag, str):
                if sub_item.tag.lower() == "pref":
                    (c_name, c_type, c_value) = parse_config_item(sub_item)
                    global_misc[c_name] = (c_name, c_type, c_value)

                if sub_item.tag.lower() == "action":
                    action = self._parse_action(sub_item)
                    default = sub_item.get("DEFAULT")
                    if not default:
                        raise ValueError(
                            "Auction Parser Error: missing name at line {0}".format(str(sub_item.sourceline)))
                    else:
                        action.default_action = ParseFormats.parse_bool(default)
                    global_actions[action.name] = action

        return global_misc, global_actions

    @staticmethod
    def _parse_field(node: Element, field_container: IpapFieldContainer):
        """
        Parse a field from the auction xml

        :param node: node that represents the field in the xml
        :return
        """
        field_name = node.get("NAME")
        field_def_manager = FieldDefManager()
        field_def = field_def_manager.get_field(field_name)
        auction_template_field = AuctionTemplateField(field_def, field_def.Length)
        belogs_to = []
        for item in node.iterchildren():
            if isinstance(item.tag, str):
                if item.tag == "TEMPLATE_FIELD":
                    object_type = super.parse_object_type(item.get("OBJECT_TYPE"))
                    template_type = super.parse_template_type(object_type, item.get("TEMPLATE_TYPE"))
                    belogs_to.append((object_type, template_type))

        auction_template_field.field_belong_to = belogs_to
        return auction_template_field

    def _parse_auction(self, node: Element, global_set: str, global_misc_config: dict,
                       global_actions: dict, field_container: IpapFieldContainer):
        """
        Parses an auction node in the xml.

        :param node: Element  element to parse
        :param global_set: str global set
        :param global_misc_config: dict  dictionary with miscelaneous field configurations.
        :param global_actions: dict  dictionary with actions
        :param field_container: IpapFieldContainer container with all fields in the system.
        :return:
        """
        # get the Id property
        # deep copy global dictionaries, so we can overide them
        misc_config = deepcopy(global_misc_config)
        actions = deepcopy(global_actions)

        auction_id = node.get("ID").lower()
        (set_name, name) = IpapMessageParser.parse_name(auction_id)
        if not set_name:
            if global_set.isnumeric():
                set_name = global_set
            else:
                set_name = str(self.domain)

        # Get Resource set and resource Id
        resurce_set = node.get("RESOURCE_SET").lower()
        resource_id = node.get("RESOURCE_ID").lower()

        templ_fields = []

        # Iterates over children nodes
        for subitem in node.iterchildren():
            if isinstance(subitem.tag, str):
                if subitem.tag.lower() == "PREF":
                    (name, type, value) = parse_config_item(subitem)
                    misc_config[name] = (name, type, value)

                elif subitem.tag.lower() == "FIELD":
                    templ_fields.append(self._parse_field(subitem, field_container))

                elif subitem.tag.lower() == "ACTION":
                    action = self._parse_action(subitem)
                    action.default_action = True  # This is the default action,
                    actions[action.name] = action

        # get the default action
        action_default = None
        for action in actions:
            if action.default_action:
                action_default = action

        auction_key = set_name + '.' + name
        resource_key = resurce_set + '.' + resource_id
        auction = Auction(auction_key, resource_key, action_default, misc_config, templ_fields)
        return auction

    def parse(self, file_name: str) -> list:
        """
        parse the auction with the file given as parameter
        :param file_name file name including the absolute path of te file to parse.

        :return: list of auctions in the file
        """
        config = Config().get_config()

        the_dtd = config['AuctionfileDtd']
        root_node = config['DtdRootNode']

        parser = etree.XMLParser(dtd_validation=True)
        base_dir = pathlib.Path(__file__).parent.parent
        the_dtd = base_dir / 'xmls' / the_dtd

        if not os.path.exists(the_dtd):
            raise ValueError("The DTD ({}) does not exist!".format(the_dtd))

        with open(the_dtd) as dtd_file:
            dtd = etree.DTD(dtd_file)
            tree = etree.parse(file_name)
            valid = dtd.validate(tree)

            if not valid:
                raise ValueError("XML given is invalid!")

            root = tree.getroot()
            g_set = root.get('ID').lower()

            ipap_field_container = IpapFieldContainer()
            ipap_field_container.initialize_reverse()
            ipap_field_container.initialize_forward()

            auctions = []
            for item in root.iterchildren():
                if isinstance(item.tag, str):  # Only it takes xml nodes (remove comments).
                    if item.tag.lower() == "global":
                        (global_misc_config, global_actions) = self._parse_global_options(item)
                    elif item.tag.lower() == "auction":
                        auction = self._parse_auction(item, g_set, global_misc_config,
                                                      global_actions, ipap_field_container
                                                      )
                        auctions.append(auction)

            return auctions


def parse_config_item(item: Element) -> (str, str, str):
    """
    Parse a configuration item.

    :param item: item to be parsed.
    :return
    """
    c_name = item.get("NAME")
    c_value = item.text
    if not c_name:
        raise ValueError("The xml has a preference with no name")

    if not c_value:
        raise ValueError("The xml has a preference with no value")

    c_name = c_name.lower()

    c_type = item.get("TYPE")
    if c_type:
        c_type = c_type.lower()
    else:
        c_type = "string"  # default type is string.

    ParseFormats.parse_item(c_type, c_value)
    return c_name, c_type, c_value


if __name__ == "__main__":
    auction_xml_file_parser = AuctionXmlFileParser(10)
    auction_xml_file_parser.parse("/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions1.xml")
