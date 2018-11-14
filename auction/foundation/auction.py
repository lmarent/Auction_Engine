#auction.py
from datetime import datetime
from auctioning_object import AuctioningObject, AuctioningObjectType

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

    def _build_templates():
        pass

    def __init__(self, key, resource_key, action, misc_dict, template_data_id=0, 
                 template_option_id=0):
        
        super(Auction).__init__(key, AuctioningObjectType.AUCTION)
        self.resource_key = resource_key
        self.action = action
        self.misc_dict = misc_dict

        self._build_interval()
        
        # TODO: Complete the code
        self._build_templates()

        self.template_data_id = template_data_dd    
        self.template_option_id = template_option_id
        self.sessions = {}

    def increment_session_references(self,session_id):

    def 
