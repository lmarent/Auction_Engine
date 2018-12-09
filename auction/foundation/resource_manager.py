from foundation.resource import Resource
from foundation.auctioning_object_manager import AuctioningObjectManager


class ResourceManager(AuctioningObjectManager):

    def __init__(self, domain: int):
        super(ResourceManager, self).__init__(domain)
        self.time_idx = {}

    def add_resource(self, resource: Resource):
        """
        Adds a resource from the container

        :param resource: resource to add
        """
        super.add_auctioning_object(resource)

    def delete_resource(self, resource_key : str):
        """
        Deletes a resource from the container

        :param resource_key: resource key to delete
        :return:
        """
        super.del_actioning_object(resource_key)

    def get_resource(self, resource_key:str) ->Resource:
        """
        gets a resource from the container

        :param resource_key: resource key to get
        :return: Resource or an exception when not found.
        """
        return super.get_auctioning_object(resource_key)