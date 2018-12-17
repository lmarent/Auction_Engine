import os
import importlib
import importlib.util
from foundation.module import Module


class ModuleLoader:
    """
    The Module loader class maintains modules loaded during the execution of a bidding process. There are two
    kinds of modules. Modules to be executed on customer agents which are thse that create bids and module for
    execution on servers, which are those that take bids an create allocations.

    Atttributes
    -----------
    group: configuration group
    modules: dict  map of modules already loaded.
    """

    def __init__(self, module_directory:str, group: str,  modules: str ):
        self.group = group
        self.modules = {}

        if not module_directory:
            raise ValueError("ModuleLoader: invalid empty module directory")

        # adds '/' if dir does not end in one already
        if module_directory[len(module_directory)-1] != '/':
            module_directory += "/"

        # test if specified dir does exist
        if not os.path.isdir(module_directory):
            raise ValueError("ModuleLoader: invalid module directory {0}".format(module_directory))

        self.module_directory = module_directory

        # loads modules included in the list. We expect the list separated by comma(,)
        if modules:
            names = modules.split(',')
            for name in names:
                self.load_module(name, True)

    def load_module(self, module_name: str, preload: bool) -> Module:
        """
        Loads a specific module
        :param module_name: module name to be loaded
        :param preload: if it is loaded at the start of the auctioner
        :return module loaded
        """
        if not module_name:
            raise ValueError("Invalid module name, it is empty")

        # the module name is relative
        if '/' not in module_name:
            if module_name.endswith('.py'):
                file_name = self.module_directory + module_name
            else:
                file_name = self.module_directory + module_name + '.py'

        # Check if the module can be imported
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            module_class =  getattr(module, module_name)
            klass = module_class(module_name,file_name, module_name, module)
            self.modules[module_name] = klass
            return module
        except FileNotFoundError as e:
            raise ModuleNotFoundError("The module with name {0} can not be open".format(file_name))

    def get_module(self, module_name:str):
        """
        Gets the module from the module loader

        :param module_name: name of the module to get.
        """
        if not module_name:
            raise ValueError('no module name specified')

        if module_name in self.modules:
            module = self.modules[module_name]
        else:
            module = self.load_module(module_name, False)

        module.link()
        return module


    def release_module(self, module_name: str):
        """
        Release the module from the module louder
        :param module_name name of the module to release.

        """
        if module_name in self.modules:
            module = self.modules[module_name]
            module.unlink()
            if module.get_references() <= 0:
                self.modules.pop(module_name, None)

