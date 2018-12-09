

class AuctionProcessObject():
    """
     Manages and applies agent processing functions

     Attributes
     ----------
     key: int : index for uniquely identify this process object.
     module: ProcModule Module loaded to execute the process
     process_api: Module Api.
    """

    def __init__(self,key=0, module=None, process_api=None):
        self.key=key
        self.module=module
        self.process_api=process_api

    def set_module(self,module):
        """
        Sets the module to execute

        :param module:
        """
        self.module = module

    def set_process_api(self, process_api):
        """
        Sets the process api to be used during execution.

        :param process_api:
        """
        self.process_api = process_api

    def get_key(self) -> int:
        """
        Returns the key used to identify the auction process object
        :return:
        """
        return self.key

    def get_module(self):
        """
        Gets the module
        :return:
        """
        return self.module

    def get_process_api(self):
        """
        Gets the process api
        :return:
        """
        return self.process_api