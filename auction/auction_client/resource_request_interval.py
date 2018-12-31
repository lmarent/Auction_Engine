from foundation.interval import Interval
from foundation.auctioning_object import AuctioningObjectState


class ResourceRequestInterval(Interval):

    def __init__(self):
        super.__init__(ResourceRequestInterval, self).__init__()
        self.state: AuctioningObjectState = AuctioningObjectState.NEW
        self.resource_request_process = set()

    def add_resource_request_process(self, resource_request_process_key: str):
        """

        :param resource_request_process_key:
        :return:
        """
        self.resource_request_process.add(resource_request_process_key)

    def delete_resource_request_process(self,resource_request_process_key: str):
        """

        :param resource_request_process_key:
        :return:
        """
        self.resource_request_process.discard(resource_request_process_key)
