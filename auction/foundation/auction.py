# auction.py
from datetime import datetime
from lxml.etree import Element

from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType
from foundation.template_id_source import TemplateIdSource
from foundation.interval import Interval
from foundation.config_param import ConfigParam

from python_wrapper.ipap_field_container import IpapFieldContainer
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_template import TemplateType
from python_wrapper.ipap_template import UnknownField
from python_wrapper.ipap_template import ObjectType


class Action:
    """
    Class for describing the action to be performed everytime that the auction should be triggered

    Attributes
    ----------

    name: String
        Name of the procedure to be performed
    default_action: Boolean
        defines whether or not this action is the default one for the auction
    config_dict: dict 
        configuration tuple to be used to start the action.
    """

    def __init__(self, name: str, default_action: bool, config_dict: dict):
        self.name = name
        self.default_action = default_action
        self.config_dict = config_dict

    def add_config_item(self, config_param: ConfigParam):
        """
        Adds a configuration item to the action

        :param config_param: configuration parameter to add
        """
        self.config_dict[config_param.name] = config_param

    def get_config_item(self, name: str) -> ConfigParam:
        """
        Gets a configuration item
        :param name: name of the confoguration item to find.
        :return: tuple (name, type, and value )
        """
        if name in self.config_dict:
            return self.config_dict[name]
        else:
            ValueError("Name {0} was not found in the configuration dictionary".format(name))

    def get_config_params(self) -> dict:
        """
        Returns the configuration params to be used during action initialization.

        :return: dictinary with name - param definition
        """
        return self.config_dict

    def get_name(self) -> str:
        """
        Returns the name of the module to be used.

        :return: module's name
        """
        return self.name

    def parse_action(self, node: Element):
        """
        parsers an action from a xml element.
        :param node: xml node.
        """

        action_name = node.get("NAME").lower()

        # Verifies that a name was given to the action.
        if not action_name:
            raise ValueError("Auction Parser Error: missing name at line {0}".format(str(node.sourceline)))

        self.name = action_name

        for item in node.iterchildren():
            if isinstance(item.tag, str):
                if item.tag.lower() == "pref":
                    config_param = ConfigParam()
                    config_param.parse_config_item(item)
                    self.add_config_item(config_param)


class AuctionTemplateField:
    def __init__(self, field=None, size=0):
        self.field = field  # This is of type FieldDefinition
        self.size = size
        self.field_belong_to = list()  # list of tuples (object type, template_type)

    def set_field(self, field):
        self.field = field

    def set_size(self, size):
        self.size = size

    def add_belonging_tuple(self, object_type: ObjectType, template_type: TemplateType):
        self.field_belong_to.append((object_type, template_type))


class Auction(AuctioningObject):
    """
    Class for describing an auction in the system. An auction should be created everytime
    that we have a different combination between data,option templateand algorithm. 
    
    Attributes:
    -----------
    key: String
       unique identifier for the auction within the system
    resource_key: String
       unique identifier for the resource being auctioned
    start: DateTime
       start datatime for the auction in the system
    stop: DateTime
       stop datatime for the auction in the system
    interval: Interval
       defines the interval during for auction execution 
    template_data_id: Integer
        Identifier of the template for data using the auction
    template_option_id: Integer
        Identifier of the template for options using the auction
    action: Action
        Action to be performed everytime that the auction should be started.
    misc_dict: dict
        miscelaneous pairs including start, stop, duration, interval, align
	"""
    def __init__(self, key: str, resource_key: str, action: Action, misc_dict: dict):
        super(Auction, self).__init__(key, AuctioningObjectType.AUCTION)
        self.resource_key = resource_key
        self.action = action
        self.misc_dict = misc_dict
        self.bidding_object_templates = {}
        self.template_data_id = -1
        self.template_option_id = -1
        self.sessions = set()
        self._build_interval()

    @staticmethod
    def get_misc_value(misc_item: ConfigParam):

        if misc_item is None:
            return None
        else:
            return misc_item.value

    def _build_interval(self):
        """
        Builds intervals when the auction is going to be performed
        """
        # A miscelaneous item is a tuple of three components, name, type and value
        misc_start = self.misc_dict.get('start', None)
        sstart = self.get_misc_value(misc_start)

        misc_stop = self.misc_dict.get('stop', None)
        sstop = self.get_misc_value(misc_stop)

        misc_duration = self.misc_dict.get('duration', None)
        sduration = self.get_misc_value(misc_duration)

        misc_interval = self.misc_dict.get('interval', None)
        sinterval = self.get_misc_value(misc_interval)

        misc_align = self.misc_dict.get('align', None)
        salign = self.get_misc_value(misc_align)

        interval_dict = {
            'start': sstart, 'stop': sstop, 'duration': sduration,
            'interval': sinterval, 'align': salign
        }

        startatleast = datetime.now()
        self.interval = Interval()
        self.interval.parse_interval(interval_dict, startatleast)

    def set_data_auction_template(self, tid: int):
        """
        Sets the data auction template
        :param tid: template identifier
        """
        self.template_data_id = tid

    def set_option_auction_template(self, tid: int):
        """
        Sets the option auction template
        :param tid: template identifier
        """
        self.template_option_id = tid

    def set_bidding_object_template(self, object_type: ObjectType, templ_type: TemplateType, template_id: int):
        """
        Sets a new bigging object template for the auction. Valid bidding objects includes bid, allocations.
        :param object_type: object type (i.e., bid, allocation)
        :param templ_type:  template's types (data, options)
        :param template_id: template identifier
        """
        if object_type not in self.bidding_object_templates:
            self.bidding_object_templates[object_type] = {}

        self.bidding_object_templates[object_type][templ_type] = template_id

    def build_templates(self, templ_fields: dict)-> list:
        """
        Build templates being used for the auction.
        :param templ_fields:        fields to be used by the auction within each template
        :return list of templates
        """
        field_container = IpapFieldContainer()
        field_container.initialize_forward()
        field_container.initialize_reverse()

        templates_ret = []

        # Creates the auction data template
        auct_template = self.create_auction_template(field_container, TemplateType.IPAP_SETID_AUCTION_TEMPLATE)
        self.set_data_auction_template(auct_template.get_template_id())
        templates_ret.append(auct_template)

        # Creates the option auction template
        opt_auct_template = self.create_auction_template(field_container, TemplateType.IPAP_OPTNS_AUCTION_TEMPLATE)
        self.set_option_auction_template(opt_auct_template.get_template_id())
        templates_ret.append(opt_auct_template)

        # Insert other templates related to bidding objects.
        for object_type in range(1, ObjectType.IPAP_MAX_OBJECT_TYPE.value):
            templ_type_list = auct_template.get_object_template_types(ObjectType(object_type))
            for templ_type in templ_type_list:
                mandatory_fields = auct_template.get_template_type_mandatory_field(templ_type)
                template = self.create_bidding_object_template(templ_fields, field_container,
                                                               mandatory_fields, ObjectType(object_type), templ_type
                                                               )

                # Add a local reference to the template.
                self.set_bidding_object_template(ObjectType(object_type), templ_type, template.get_template_id())

                # Insert the template in the general container.
                templates_ret.append(template)
        return templates_ret

    @staticmethod
    def add_template_field(template: IpapTemplate, ipap_field_container: IpapFieldContainer, eno: int,
                           ftype: int):
        """
        Adds a new field to a template
        :param template:                Template where we are going to add the field
        :param ipap_field_container:    field container where we maintain the possible fields
        :param eno:                     enterprise number identifier
        :param ftype:                   id of the field for the ipap_message
        """
        # By default network encoding
        encode_network = True

        field = ipap_field_container.get_field(eno, ftype)
        size = field.get_length()
        template.add_field(size, UnknownField.KNOWN, encode_network, field)

    def create_auction_template(self, field_container, template_type: TemplateType) -> IpapTemplate:
        """
        Create an auction template based on its mandatory fields

        :rtype: IpapTemplate
        :param field_container: container with all possible fields defined
        :param template_type:   Type of template to use.
        :return: template created.
        """
        template_source_id = TemplateIdSource()

        # Create the bid template associated with the auction
        template = IpapTemplate()
        list_fields = template.get_template_type_mandatory_field(template_type)
        template.set_id(template_source_id.new_id())
        template.set_max_fields(len(list_fields))
        template.set_type(template_type)

        for i in range(0, len(list_fields)):
            self.add_template_field(template, field_container, list_fields[i].get_eno(), list_fields[i].get_ftype())

        return template

    @staticmethod
    def calculate_template_fields(object_type: ObjectType, templ_type: TemplateType, templ_fields: dict,
                                  mandatory_fields: list) -> dict:
        """
        Creates the sets of fields to be used in a template. The set includes mandatory and those that have been chosen
        by the user for the auction
        :param object_type          Object type
        :param templ_type:          Template type (data, options)
        :param templ_fields:        Field to include given by the user
        :param mandatory_fields:    Mandatory fields to include given by the template type
        :return: dictionary with key and field key
        """

        dict_return = {}
        # 1. insert the template mandatory fields.
        for field in mandatory_fields:
            dict_return[field.get_key()] = field

        # 2. insert other configurated fields.
        for field_key in templ_fields:
            include = False

            field = templ_fields[field_key]
            for (object_type_field, templ_type_field) in field.field_belong_to:
                if (object_type_field == object_type) and (templ_type_field == templ_type):
                    include = True
                    break

            if include:
                field_key = IpapFieldKey(field.field['eno'], field.field['ftype'])
                # Excludes field_keys already in the dictionary.
                if field_key.get_key() not in dict_return.keys():
                    dict_return[field_key.get_key()] = field_key

        return dict_return

    def create_bidding_object_template(self, templ_fields: dict,
                                       field_container: IpapFieldContainer,
                                       mandatory_fields: list,
                                       object_type: ObjectType,
                                       templ_type: TemplateType) -> IpapTemplate:
        """
        Create a bidding object template
        :param templ_fields:        Fields to include given by the user
        :param field_container:     Container with all possible fields defined in the ipap_message
        :param mandatory_fields:    Mandatory fields to include given by the template type
        :param object_type:         object type (i.e., bid, allocation)
        :param templ_type:          template's types (data, options)
        :return: a new template
        """
        template_source_id = TemplateIdSource()

        field_keys = self.calculate_template_fields(object_type, templ_type, templ_fields, mandatory_fields)

        # Create the bid template associated with the auction
        template = IpapTemplate()
        template.set_id(template_source_id.new_id())
        template.set_max_fields(len(field_keys))
        template.set_type(templ_type)

        for key in field_keys:
            field_key = field_keys[key]
            self.add_template_field(template, field_container, field_key.get_eno(), field_key.get_ftype())

        return template

    def get_auction_data_template(self) -> int:
        """
        Gets the identifier of the auction data template
        :return: integer representing the auction data template
        """
        return self.template_data_id

    def get_option_auction_template(self):
        """
        Gets the identifier of the auction option template
        :return: integer representing the auction option template
        """
        return self.template_option_id

    def get_bidding_object_template(self, object_type: ObjectType, templ_type: TemplateType ) -> int:
        """
        Gets the identifier of a bidding object template
        :param object_type: The object type (i.e., bid, allocation) for which we want to get the template
        :param templ_type:  The template type for which we want to get the template.

        :return: integer representing the template's identifier
        """

        if object_type in self.bidding_object_templates:
            if templ_type in self.bidding_object_templates[object_type]:
                return self.bidding_object_templates[object_type][templ_type]
            else:
                return 0
        return 0

    def add_session_reference(self, session_id: str):
        """
        Associates a new session as referencing this auction
        :param session_id: session id referencing this auction
        """
        self.sessions.add(session_id)

    def delete_session_reference(self, session_id: str):
        """
        Disassociates a session as referencing this auction
        :param session_id: session id referencing this auction
        """
        self.sessions.discard(session_id)

    def set_start(self, start: datetime):
        """
        Sets the start datatime for the auction
        :param start: start datetime
        :return:
        """
        self.interval.start = start

    def get_start(self) -> datetime:
        """
        Gets the start datetime for the auction
        :return:
        """
        return self.interval.start

    def get_stop(self):
        """
        Gets the stop datetime for the auction
        :return:
        """
        return self.interval.stop

    def set_stop(self, stop: datetime):
        """
        Sets the stop datetime for the auction

        :param stop: stop datetime
        :return:
        """
        self.interval.stop = stop

    def get_resource_key(self) -> str:
        """
        Gets the resource key from the auction
        :return: string representing the resource key.
        """
        return self.resource_key

    def get_action(self) -> Action:
        """
        Gets the action associated with the auction
        :return: Action
        """
        return self.action

    def get_interval(self) -> Interval:
        """
        Gets the interval associated with the auction
        :return:
        """
        return self.interval

    def get_session_references(self):
        return len(self.sessions)

    def get_template_list(self) -> str:
        """
        Gets the list of templates applicable for the auction.
        :return:list of template ids separated by comma.
        """
        first_time: bool  = True
        template = IpapTemplate()
        ret = ""

        for object_type in range(1, ObjectType.IPAP_MAX_OBJECT_TYPE.value):

            list_templates = template.get_object_template_types(ObjectType(object_type));
            for templ_type in list_templates:
                template_id = self.get_bidding_object_template( ObjectType(object_type), templ_type)
                if first_time:
                    ret = ret + "{0}".format(str(template_id))
                    first_time = False
                else:
                    ret = ret + ",{0}".format(str(template_id))

        return ret

    def intersect_interval(self, start: datetime, stop: datetime):
        """
        Enlarge the interval whenever the interval defined by the start and stop time for the auction is shorter
        than the given interval.

        :param start: start time
        :param stop: stop time
        """
        if start <= self.interval.start:
            self.interval.start = start

        if self.interval.stop <= stop:
            self.interval.stop = stop

    def get_module_name(self):
        """
        Returns the name of the module to be used to perform this auction
        :return: module's name
        """
        return self.action.name

