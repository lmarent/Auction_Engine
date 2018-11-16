#auction.py
from datetime import datetime
from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType
from foundation.template_id_source import TemplateIdSource

from python_wrapper.ipap_field_container import IpApFieldContainer
from python_wrapper.ipap_template import IpapTemplate
from python_wrapper.ipap_template_container import IpapTemplateContainer
from python_wrapper.ipap_field_key import IpapFieldKey
from python_wrapper.ipap_template import IPAP_SETID_AUCTION_TEMPLATE
from python_wrapper.ipap_template import IPAP_OPTNS_AUCTION_TEMPLATE
from python_wrapper.ipap_template import KNOWN
from python_wrapper.ipap_template import IPAP_MAX_OBJECT_TYPE



class Action:
    """
    Class for describingthe action to be perform everytime that the auction should be trrigered

    Attributes
    ----------

    name: String
        Name of the procedure to be performed
    default_action: Boolean
        defines whether or not this action is the defaut one for the auction
    config_dict: dict 
        configuration value pairs to be used to start the action. 
    """

    def __init__(self, name, default_action, config_dict):
        self.name = name
        self.default_action = default_action
        self.config_dict = config_dict

class AuctionTemplateField():
    def __init__(self, field=None,size=0):
        self.field = field
        self.size = size
        self.field_belong_to = list() # list of tuples (object type, template_type)

    def set_field(self, field):
        self.field = field

    def set_size(self, size):
        self.size = size

    def add_belonging_tuple(self, object_type : int, template_type: int):
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


    def __init__(self, key, resource_key, action, misc_dict,
                    templ_fields: dict, template_container : IpapTemplateContainer):
        
        super(Auction).__init__(key, AuctioningObjectType.AUCTION)
        self.resource_key = resource_key
        self.action = action
        self.misc_dict = misc_dict
        self.bidding_object_templates = {}
        self.template_data_id = -1
        self.template_option_id = -1
        self.sessions = set()

        self._build_interval()

        # TODO: Complete the code
        self._build_templates(templ_fields, template_container)

    def _build_interval(self):
        sstart = self.misc_dict['start']
        sstop = self.misc_dict['start']
        sduration = self.misc_dict['duration']
        sinterval = self.misc_dict['interval']
        salign = self.misc_dict['align']

        interval_dict = {
            'start' : sstart, 'stop' : sstop, 'duration' : sduration,
            'interval' : sinterval, 'align' : salign
            }

        startatleast = datetime.now()
        self.interval = Interval()
        self.interval.parse_interval(interval_dict, startatleast)

    def set_data_auction_template(self, tid: int):
        self.template_data_id = tid


    def set_option_auction_template(self, tid :int):
        self.template_option_id = tid

    def set_bidding_object_template(self, object_type : int, templ_type : int, template_id : int):
        if object_type not in self.bidding_object_templates:
            self.bidding_object_templates[object_type] = {}
        template_object = self.bidding_object_templates[object_type]
        template_object[templ_type] = template_id

    def _build_templates(self, templ_fields : dict, template_container : IpapTemplateContainer):
        field_container = IpApFieldContainer()
        field_container.initialize_forward()
        field_container.initialize_reverse()

        # Creates the auction data template
        auctTemplate = self.create_auction_template(field_container, IPAP_SETID_AUCTION_TEMPLATE)
        self.set_data_auction_template(auctTemplate.get_template_id())
        template_container.add_template(auctTemplate)

        # Creates the option auction template
        optAuctTemplate = self.create_auction_template(field_container, IPAP_OPTNS_AUCTION_TEMPLATE)
        self.set_option_auction_template(optAuctTemplate.get_template_id())
        template_container.add_template(optAuctTemplate)

        # Insert other templates related to bidding objects.
        for object_type in range (1, IPAP_MAX_OBJECT_TYPE):
            templ_type_list = auctTemplate.get_object_template_types(object_type)
            for templ_type in templ_type_list:
                mandatory_fields = auctTemplate.get_template_type_mandatory_field(templ_type)
                template = self.create_bidding_object_template(templ_fields, field_container,
                                                          mandatory_fields, object_type , templ_type
                                                          )

                # Add a local reference to the template.
                self.set_bidding_object_template(object_type, templ_type, template.get_template_id())

                # Insert the template in the general container.
                template_container.add_template(template)

    def add_template_field(self, template : IpapTemplate, ipap_field_container : IpApFieldContainer, eno : int, ftype: int ):

        # By default network encoding
        encodeNetwork = 1

        field = ipap_field_container.get_field(eno, type)
        size = field.get_length()
        template.add_field(size, KNOWN, encodeNetwork, field);


    def create_auction_template(self, field_container, template_type):
        """
        Create an auction template based on its mandatory fields

        :param field_container: container with all possible fields defined
        :param template_type:   Type of template to use.
        :return: template created.
        """

        template_source_id = TemplateIdSource()

        # Create the bid template associated with the auction
        template = IpapTemplate()
        list_fields = template.get_template_type_mandatory_field(1)
        template.set_id(template_source_id.new_id())
        template.set_max_fields(len(list_fields))
        template.set_type(template_type)

        for i in range (0, len(list_fields)):
            self.add_template_field(template, field_container, list_fields[i].get_eno(), list_fields[i].get_ftype())

        return template


    def calculate_template_fields(object_type : int, templ_type : int, templ_fields : dict, mandatory_fields : list ) -> dict:

        dict_return = {}
        # 1. insert the template mandatory fields.
        for field in mandatory_fields:
            dict_return[field.get_key()] = field

        # 2. insert other configurated fields.
        for field_key in templ_fields:
            include = False

            field = templ_fields[field_key]
            for (object_type_field,templ_type_field) in field.belogsto:
                if (object_type_field == object_type) and (templ_type_field == templ_type):
                    include = True
                    break

            if include:
                field_key = IpapFieldKey(field.get_eno(), field.get_ftype())
                # Excludes field_keys already in the dictionary.
                if field_key.get_key() not in dict_return.keys()
                    dict_return[field_key.get_key()] = field_key

        return dict_return


    def create_bidding_object_template(self, templ_fields : dict,
                                       field_container : IpApFieldContainer,
                                       mandatory_fields: list,
                                       object_type : int,
                                       templ_type : int ) -> IpapTemplate:
        template_source_id = TemplateIdSource()

        field_keys = self.calculate_template_fields(object_type, templ_type, templ_fields, mandatory_fields)

        # Create the bid template associated with the auction
        template = IpapTemplate()
        template.set_id( template_source_id.new_id() )
        template.set_maxfields( len(field_keys) )
        template.set_type(templ_type)

        for key in field_keys:
            field_key = field_keys[key]
            self.add_template_field(template, field_container, field_key.get_eno(), field_key.get_ftype())

        return template

    def get_auction_data_template(self):
        return self.template_data_id

    def get_option_auction_template(self):
        return self.template_option_id

    def get_bidding_object_template(self, object_type, templ_type):
        if object_type in self.bidding_object_templates:
            if templ_type in self.bidding_object_templates[object_type]
                return self.bidding_object_templates[object_type][templ_type]
            else:
                return 0
        return 0


    def add_session_reference(self, session_id : str):
        self.sessions.add(session_id)

    def delete_session_reference(self, session_id : str):
        self.sessions.discard(session_id)
