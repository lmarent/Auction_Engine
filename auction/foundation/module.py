from abc import ABCMeta

def function1():
    print('aqui estoy')

class Module(metaclass=ABCMeta):
    """
    this class represents the base class for auction processing modules
    """
    def __init__(self, module_name:str , file_name:str , lib_handle):
        self.module_name = module_name
        self.file_name = file_name
        self.lib_handle = lib_handle
        self.refs = 0
        self.calls = 0

    def return_func(self, func_name:str):
        """
        Gets the function to be teh executed.
        :param func_name: function name to obtain
        :return: Function object.
        """
        return getattr(self.lib_handle, func_name)