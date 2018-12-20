# resource_request_manager.py
from foundation.auctioning_object_manager import AuctioningObjectManager
from auction_client.resource_request import ResourceRequest

class ResourceRequestManager(AuctioningObjectManager):

    def __init__(self):
        super(ResourceRequestManager, self).__init__()
        self.map_by_start_date = {}
        self.map_by_end_date = {}
        pass

    def get_resource_request(self, resource_request_key: str):
        """
        gets a resource request from the container
        :param resource_request_key: resource request key to get
        :return: Resource request or an exception when not found.
        """
        return super(ResourceRequestManager, self).get_auctioning_object(resource_request_key)

    def add_resource_requests(self, resource_requests: list):
        """
        Adds a list of resource requests to the container

        :param resource_requests: resource request list to add
        :return:
        """
        for request in resource_requests:
            self.add_resource_request(request)

    def add_resource_request(self, resource_request: ResourceRequest):
        """
        Adds a resource request to the container

        :param resource_request: resource request to add
        """
        super(ResourceRequestManager, self).add_auctioning_object(resource_request)
         
        # Inserts the intervals of the resource request
        intervals = resource_request.get_intervals()
        for interval in intervals:
            if interval.start not in interval.start:
                self.map_by_start_date[interval.start] = []
            self.map_by_start_date[interval.start].append(resource_request)

            if interval.stop:
                if interval.stop not in self.map_by_end_date:
                    self.map_by_end_date[interval.stop] = []
                self.map_by_end_date[interval.stop].append(resource_request)

    def del_resource_request(self, resource_request_key:str):
        """
        Deletes a resource request from the container

        :param resource_request_key: resource request key to delete
        :return:
        """
        super(ResourceRequestManager, self).del_actioning_object(resource_request_key)

    def parse_resource_request_from_file(self, file_name:str) -> list:
        """
        parse a XML resource request from file
        :param file_name: file to parse.
        :return: list of resource request parsed.
        """
