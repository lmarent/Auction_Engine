#auction.py
from datetime import datetime
from foundation.auctioning_object import AuctioningObject
from foundation.auctioning_object import AuctioningObjectType
from python_wrapper.ipap_field_container import IpApFieldContainer
from python_wrapper.ipap_template import IpapTemplate


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


    def __init__(self, key, resource_key, action, misc_dict, template_data_id=0, 
                 template_option_id=0):
        
        super(Auction).__init__(key, AuctioningObjectType.AUCTION)
        self.resource_key = resource_key
        self.action = action
        self.misc_dict = misc_dict

        self._build_interval()
        
        # TODO: Complete the code
        self._build_templates()

        self.template_data_id = template_data_id
        self.template_option_id = template_option_id
        self.sessions = {}

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

        startatleast = datatime.now()
        self.interval = Interval()
        self.interval.parse_interval(interval_dict, startatleast)


    def _build_templates(templFields, templateContainer):
        field_container = IpApFieldContainer()
        field_container.initialize_forward()
        field_container.initialize_reverse()

        # Creates the auction data template
        auctTemplate = create_auction_template(field_container, IPAP_SETID_AUCTION_TEMPLATE)
        setDataAuctionTemplate(auctTemplate.get_template_id())
        templateContainer.add_template(auctTemplate)

        # Creates the option auction template
        optAuctTemplate = create_auction_template(field_container, IPAP_OPTNS_AUCTION_TEMPLATE)
        setOptionAuctionTemplate(optAuctTemplate.get_template_id())
        templateContainer.add_template(optAuctTemplate)

        # Insert other templates related to bidding objects.
        i = 0;
        for (i = 1; i < IPAP_MAX_OBJECT_TYPE; i++){

            set < ipap_templ_type_t > templSet = ipap_template::
            getObjectTemplateTypes((ipap_object_type_t)
        i);
        set < ipap_templ_type_t >::iterator iter;
        for (iter = templSet.begin(); iter != templSet.end(); ++iter ){

        ipap_template * templ =
        createBiddingObjectTemplate(templFields, g_ipap_fields,
        (ipap_object_type_t) i, * iter );

        # Add a local reference to the template.
        setBiddingObjectTemplate((ipap_object_type_t) i, * iter, templ->get_template_id());

        # Insert the template in the general container.
        templateContainer->add_template(templ);
        }
        }

    def add_template_field(self, template : IpapTemplate, ipap_field_container : IpApFieldContainer, eno : int, ftype: int ):

        # By default network encoding
        encodeNetwork = 1

        field = ipap_field_container.get_field(eno, type)
        size = field.get_length()
        template.add_field(size, KNOWN, encodeNetwork, field);


    def create_auction_template(self, field_container, template_type):

        # Create the bid template associated with the auction

        template_source_id = TemplateIdSource.getInstance()

        template = IpapTemplate()
        list_fields = template.get_template_type_mandatory_field(1)
        template.set_id(template_source_id.new_id())
        template.set_max_fields(len(list_fields))
        template.set_type(template_type)

        for i in range (0, len(list_fields)):
            self.add_template_field(template, g_ipap_fields, list_fields[i].get_eno(), list_fields[i].get_ftype())

    return templ;



    def increment_session_references(self,session_id):

    def 
