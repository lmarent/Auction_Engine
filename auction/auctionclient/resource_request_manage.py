# resource_request_manager.py
from foundation.auctioning_object_manager import AuctioningObjectManager
from auction_client_handler import handle_activate_resource_request_interval

class ResourceRequestManager(AuctioningObjectManager):

    def __init__(self):
        super(ResourceRequestManager, self).__init__()
        self.map_by_start_date = {}
        self.map_by_end_date = {}
        pass

    def get_resource_request(self, key):

    def add_resource_requests(self, resource_requests, loop):
        for request in resource_requests:
            self.add_resource_request(request,loop)

    def add_resource_request(self, resource_request, loop):
        super.add_auctioning_object(resource_request)
         
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

        # groups resource requests with same start time
        for start in self.map_by_start_date:
            for resource_request in self.map_by_start_date[start]:
                loop.call_at(new_time, handle_activate_resource_request_interval, loop, True)


    def del_resource_request(self, resource_request, loop):


