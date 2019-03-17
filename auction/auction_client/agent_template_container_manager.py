from python_wrapper.ipap_template_container import IpapTemplateContainer
from foundation.singleton import Singleton

class AgentTemplateContainerManager(metaclass=Singleton):
    """
    This class maintains the templates used to exchange messages with different servers.
    """

    def __init__(self):
        self.template_container_objects = {}


    def add_template_container(self, domain: int, template_container: IpapTemplateContainer):
        """
        Adding new template container to the Agent Template repository. It lookup the database for
        already installed template container and store it into the database.

        :param domain:
        :param template_container:
        :return:
        """
        if domain in self.template_container_objects.keys():
            raise ValueError('Template container for domain {0} is already installed'.format(domain))
        self.template_container_objects[domain] = template_container

    def get_template_container(self, domain: int) -> IpapTemplateContainer:
        """
        lookup the database of template containers for a specific template container
        """
        if domain in self.template_container_objects.keys():
            return self.template_container_objects[domain]
        else:
            raise ValueError('Template Container {} does not exist'.format(domain))

    def del_template_container(self, domain: int):
        """
        Deleting a template container. It tests the presence of the given template container
        in the database, and it removes from the database
        """
        if domain in self.template_container_objects.keys():
            del self.template_container_objects[domain]
        else:
            raise ValueError('Template Container {} does not exist'.format(domain))
