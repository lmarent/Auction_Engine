# resource_request_manager.py
from python_wrapper.ipap_message import IpapMessage
from foundation.auctioning_object_manager import AuctioningObjectManager
from auction_client.resource_request import ResourceRequest
from auction_client.resource_request_file_parser import ResourceRequestFileParser
from auction_client.ipap_resource_request_parser import IpapResourceRequestParser
from datetime import datetime


class ResourceRequestManager(AuctioningObjectManager):

    def __init__(self, domain: int):
        super(ResourceRequestManager, self).__init__(domain=domain)
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

    def add_resource_request(self, resource_request: ResourceRequest):
        """
        Adds a resource request to the container

        :param resource_request: resource request to add
        :return dictionaries with resource request to stat and stop
        """
        super(ResourceRequestManager, self).add_auctioning_object(resource_request)

        ret_start = []
        ret_stop = []
        # Inserts the intervals of the resource request
        intervals = resource_request.get_intervals()
        for interval in intervals:
            ret_start[interval.start] = resource_request
            ret_stop[interval.stop] = resource_request

            if interval.start not in interval.start:
                self.map_by_start_date[interval.start] = []
            self.map_by_start_date[interval.start].append(resource_request)

            if interval.stop:
                if interval.stop not in self.map_by_end_date:
                    self.map_by_end_date[interval.stop] = []
                self.map_by_end_date[interval.stop].append(resource_request)

        return ret_start, ret_stop

    def del_resource_request(self, resource_request_key: str):
        """
        Deletes a resource request from the container

        :param resource_request_key: resource request key to delete
        :return:
        """
        super(ResourceRequestManager, self).del_actioning_object(resource_request_key)

    def parse_resource_request_from_file(self, file_name: str) -> list:
        """
        parse a XML resource request from file
        :param file_name: file to parse.
        :return: list of resource request parsed.
        """
        resource_request_file_parser = ResourceRequestFileParser(self.domain)
        return resource_request_file_parser.parse(file_name)

    def get_ipap_message(self, resource_request: ResourceRequest, start: datetime,
                         resource_id: str, use_ipv6: bool, s_address_ipv4: str,
                         s_address_ipv6: str, port: int) -> IpapMessage:
        """
        gets the ipap_message that contains a request for resources
        :return:
        """
        ipap_resource_request_parser = IpapResourceRequestParser(self.domain)
        return ipap_resource_request_parser.get_ipap_message(start, resource_request,
                                                             resource_id, use_ipv6, s_address_ipv4, s_address_ipv6,
                                                             port)
