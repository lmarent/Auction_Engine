from foundation.singleton import Singleton
from python_wrapper.ipap_template_container import IpapTemplateContainerSingleton

class TemplateContainer(metaclass=Singleton):

    def __init__(self):
        self.template_container = None

    def get_template_container(self) -> IpapTemplateContainerSingleton:
        """
        Returns the template container defined for the agent.
        :return: IpapTemplateContainer.
        """
        if self.template_container == None:
            self.template_container = IpapTemplateContainerSingleton()

        return self.template_container

