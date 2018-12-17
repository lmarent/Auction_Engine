

class AuctionProcessObject():
    """
     Manages and applies agent processing functions

     Attributes
     ----------
     key: int : index for uniquely identify this process object.
     module: Module Module loaded to execute the process
    """

    def __init__(self,key=0, module=None):
        self.key=key
        self.module=module

    def set_module(self,module):
        """
        Sets the module to execute

        :param module:
        """
        self.module = module

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
