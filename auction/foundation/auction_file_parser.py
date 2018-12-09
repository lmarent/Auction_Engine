from lxml import etree
from lxml.etree import Element
from foundation.auction import AuctionTemplateField
from foundation.auction import Action
from foundation.auction import Auction
from foundation.field_def_manager import FieldDefManager
from foundation.ipap_message_parser import IpapMessageParser
from foundation.config import Config
from foundation.config_param import ConfigParam
from foundation.parse_format import ParseFormats
from python_wrapper.ipap_field_container import IpapFieldContainer

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
                    config_param = ConfigParam()
                    config_param.parse_config_item(sub_item)
                    global_misc[config_param.name] = config_param

                if sub_item.tag.lower() == "action":
                    action = Action("",False, dict())
                    action.parse_action(sub_item)
                    default = sub_item.get("DEFAULT")
                    if not default:
                        raise ValueError(
                            "Auction Parser Error: missing name at line {0}".format(str(sub_item.sourceline)))
                    else:
                        action.default_action = ParseFormats.parse_bool(default)
                    global_actions[action.name] = action

        return global_misc, global_actions

    def _parse_field(self, node: Element)-> (str,AuctionTemplateField):
        """
        Parse a field from the auction xml

        :param node: node that represents the field in the xml
        :return
        """
        field_name = node.get("NAME")
        field_def_manager = FieldDefManager()
        field_def = field_def_manager.get_field(field_name)
        auction_template_field = AuctionTemplateField(field_def, field_def['lenght'])
        belogs_to = []
        for item in node.iterchildren():
            if isinstance(item.tag, str):
                if item.tag.lower() == "template_field":
                    object_type = self.parse_object_type(item.get("OBJECT_TYPE").lower())
                    template_type = self.parse_template_type(object_type, item.get("TEMPLATE_TYPE").lower())
                    belogs_to.append((object_type, template_type))

        auction_template_field.field_belong_to = belogs_to
        return field_name, auction_template_field

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
        (set_name, name) = self.parse_name(auction_id)
        if not set_name:
            if global_set.isnumeric():
                set_name = global_set
            else:
                set_name = str(self.domain)

        # Get Resource set and resource Id
        resurce_set = node.get("RESOURCE_SET").lower()
        resource_id = node.get("RESOURCE_ID").lower()

        templ_fields = {}

        # Iterates over children nodes
        for subitem in node.iterchildren():
            if isinstance(subitem.tag, str):
                if subitem.tag.lower() == "pref":
                    config_param = ConfigParam()
                    config_param.parse_config_item(subitem)
                    misc_config[name] = config_param

                elif subitem.tag.lower() == "field":
                    field_name, field = self._parse_field(subitem)
                    templ_fields[field_name] = field

                elif subitem.tag.lower() == "action":
                    action = Action("",False,dict())
                    action.parse_action(subitem)
                    action.default_action = True  # This is the default action,
                    actions[action.name] = action

        # get the default action
        action_default = None
        for action_name in actions:
            if actions[action.name].default_action:
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

        if 'AuctionFileDtd' in config:
            the_dtd = config['AuctionFileDtd']
        else:
            raise ValueError("The DTD ({}) configuration option does not exist!".format('AuctionFileDtd'))

        if 'DtdRootNode' in config:
            root_node = config['DtdRootNode']
        else:
            raise ValueError("The DTD Root Node({}) configuration option does not exist!".format('DtdRootNode'))

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


if __name__ == "__main__":
    auction_xml_file_parser = AuctionXmlFileParser(10)
    auction_xml_file_parser.parse("/home/ns3/py_charm_workspace/paper_subastas/auction/xmls/example_auctions1.xml")
