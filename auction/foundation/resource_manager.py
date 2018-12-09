from foundation.resource import Resource
from foundation.auctioning_object_manager import AuctioningObjectManager
from foundation.auction import Auction


class ResourceManager(AuctioningObjectManager):

    def __init__(self, domain: int):
        super(ResourceManager, self).__init__(domain)
        self.time_idx = {}

    def add_resource(self, resource: Resource):
        """
        Adds a resource from the container

        :param resource: resource to add
        """
        super(ResourceManager, self).add_auctioning_object(resource)

    def delete_resource(self, resource_key : str):
        """
        Deletes a resource from the container

        :param resource_key: resource key to delete
        :return:
        """
        super(ResourceManager, self).del_actioning_object(resource_key)

    def get_resource(self, resource_key:str) ->Resource:
        """
        gets a resource from the container

        :param resource_key: resource key to get
        :return: Resource or an exception when not found.
        """
        return super(ResourceManager, self).get_auctioning_object(resource_key)

    def get_num_resources(self) -> int:
        """
        Returns the number of current registed resources
        :return: number of resources.
        """
        return super(ResourceManager, self).get_num_auctioning_objects()


    def verify_auction(self, auction: Auction)-> bool:
        """
        Brings the resource and verify that after inserting the auction resource intervals are still valid.

        :param auction: auction to be verified
        :return: True if correct, False Otherwise
        """

        # Bring the auction's resource key
        resource_key = auction.get_resource_key()
        try:
            resource = self.get_resource(resource_key)

            # Auction does not exist in the resource
            if resource.exist_auction(auction.get_key()):
                return False

            # If intervals are not incorrect, then returns true.
            return resource.verify_auction(auction)

        except ValueError as e:
            print('The resource given was not found, so the auction is invalid.')
            return False