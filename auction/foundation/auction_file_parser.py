from lxml import etree
from foundation.auction import AuctionTemplateField
from foundation.auction import Action
from foundation.auction import Auction
from foundation.parse_format import ParseFormats
from foundation.field_def_manager import FieldDefManager
from foundation.ipap_message_parser import IpapMessageParser
from foundation.config import Config
from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_template_container import IpapTemplateContainer

class AuctionXmlFileParser(IpapMessageParser):
    """
    This class parses file and ipap messages containing auction definitions.


    A configuration item is a tuple of three values:
        name : name of the configuration item
        type : type of the configuration item
        value: value in string.

    """

    def __init__(self, domain: int):
        super(AuctionXmlFileParser, self).__init__(domain)

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


    def _parse_action(self, node ):

        action_name = node.get("NAME").lower()

        # Verifies that a name was given to the action.
        if not action_name:
            raise ValueError("Auction Parser Error: missing name at line {0}".format(str(node.sourceline)))

        action = Action(action_name, False, dict())

        for item in node.iterchildren():
            if item.tag.lower() == "pref":
                (name, type, value) = self._parse_config_item(item)
                action.add_config_item(name, type, value)

        return action


    def _parse_global_options(self, item) -> (dict, dict):
        """
        Parse global options within the xml
        :param item: Global Tag
        :return: dictionary of configuration items.
                list of actions.
        """
        global_misc = {}
        global_actions = {}

        for sub_item in item.iterchildren():
            if sub_item.tag.lower() == "pref":
                (name, type, value) = self._parse_config_item(item)
                global_misc[name] = (name, type, value)

            if sub_item.tag.lower() == "action":
                action = self._parse_action(sub_item)
                default = sub_item.get("DEFAULT")
                if not default:
                    raise ValueError("Auction Parser Error: missing name at line {0}".format(str(sub_item.sourceline)))
                else:
                    action.default_action = ParseFormats.parse_bool(default)
                global_actions[action.name] = action

        return (global_misc, global_actions)


    def _parse_field(self, node, field_container : IpapFieldContainer):
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
                object_type = super.parse_object_type(item.get("OBJECT_TYPE"))
                template_type = super.parse_template_type(object_type, item.get("TEMPLATE_TYPE"))
                belogs_to.append((object_type, template_type))

        auction_template_field.field_belong_to = belogs_to
        return auction_template_field


    def _parse_auction(self, node, global_set :str, global_misc_config : dict,
                       global_actions :dict, field_container : IpapFieldContainer):
        """

        :param global_set:global set
        :param node:
        :return:
        """
        # get the Id property
        # deep copy global dictionaries, so we can overide them
        misc_config = global_misc_config.deepcopy()
        actions = global_actions.deepcopy()

        auction_id = node.get("ID").lower()
        (set_name, name ) = super.parse_name(auction_id)
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
            if subitem.tag.lower() == "PREF":
                (name, type, value) = self._parse_config_item(subitem)
                misc_config[name] = (name, type, value)

            elif subitem.tag.lower() == "FIELD":
                templ_fields.append(self._parse_field(subitem,field_container))

            elif subitem.tag.lower() == "ACTION":
                action = self._parse_action(subitem)
                action.default_action = True # This is the default action,
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


    def parse(self, file_name : str ) -> list:
        """
        parse the auction with the file given as parameter
        :param file_name file name including the absolute path of te file to parse.

        :return: list of auctions in the file
        """
        config = Config()
        the_dtd = config.AUCTIONFILE_DTD
        root_node = config.DTD_ROOT_NODE

        parser = etree.XMLParser(dtd_validation=True)
        dtd = etree.DTD(open(the_dtd))
        tree = etree.parse(file_name)
        valid = dtd.validate(tree)

        if (valid):
            raise ValueError("XML given is valid!")

        root = tree.getroot()
        id = root.ID.lower()

        ipap_field_container = IpapFieldContainer()
        ipap_field_container.initialize_reverse()
        ipap_field_container.initialize_forward()

        auctions = []
        global_element = root.Element("GLOBAL")

        print("Here We are")
        for item in root.iterchildren():
            if item.tag.lower() == "global":
                (global_misc_config, global_actions)  = self._parse_global_options(item)
            elif item.tag.lower() == "auction":
                auction = self._parse_auction(item, global_misc_config, global_actions, ipap_field_container)
                auctions.append(auction)

        return auctions

