#bidding_object_serializer.py

from abc import ABCMeta
from abc import abstractmethod
from foundation.template_cotainer import TemplateContainer 


class BiddingObjectSerializer(meta=ABCMeta):
    def __init__(content_type : str):
        self.content_type = content_type

    @abstractmethod
    def serialize(self, bidding_object):
        return

class BiddingObjectJsonSerializer(BiddingObjectSerializer):

    def __init__():
        super(BiddingObjectJsonSerializer).__init__("application/json")

    def _add_data_record(self, messsage, element, data_template):
        # Inserts Auction Id field
        

        # Inserts Bidding Id field
        # Inserts Record Id
        # Inserts Bidding Object Type Id
        # Inserts all fields registered within the template.

    def serialize(self, auction, bidding_object):
        data_type = bidding_object.get_type()
        data_template_id, options_template_id = auction.get_bidding_object_template()
        data_template = TemplateContainer.get_template(data_template_id)
        option_template = TemplateContainer.get_template(options_template_id)
        message = {}

        # Includes all data Records:
        for element in bidding_object.elements:
            add_data_record(messsage, element, data_template)

        # Include all options records: 
        for option in options:
            add_option_record(message, option, option_template)