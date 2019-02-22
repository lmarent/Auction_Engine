from foundation.interval import Interval
from foundation.auctioning_object import AuctioningObjectState


class ResourceRequestInterval(Interval):

    def __init__(self):
        super.__init__(ResourceRequestInterval, self).__init__()
        self.field_values = {}
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

    def get_resource_request_process(self) -> set:
        """
        Gets the resource request process associated with the interval

        :return: set of resource request
        """
        return self.resource_request_process

    def set_fields(self, config_params: dict):
        """
        Sets config params- Initially they are the same as the params given for the resource request.

        :param config_params:
        :return:
        """
        self.field_values = config_params

    def get_fields(self) -> dict:
        """
        Gets config params

        :return: dictionary with config params
        """
        return self.field_values

    def stop_execution(self):
        """
        Stops execution of resource request interval.
        :return:
        """
        pass